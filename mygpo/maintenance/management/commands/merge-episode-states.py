from optparse import make_option
from itertools import count
from functools import partial

from django.core.management.base import BaseCommand

from mygpo.utils import progress, multi_request_view
from mygpo.users.models import EpisodeUserState
from mygpo.counter import Counter
from mygpo.maintenance.merge import merge_episode_states
from mygpo.couchdb import bulk_save_retry, get_main_database


class Command(BaseCommand):
    """ Merge duplicate EpisodeUserState documents """

    option_list = BaseCommand.option_list + (
        make_option('--skip', action='store', type=int, dest='skip', default=0,
           help="Number of states to skip"),
    )

    def handle(self, *args, **options):

        skip = options.get('skip')
        total = EpisodeUserState.view('episode_states/by_user_episode',
                limit=0,
            ).total_rows
        db = get_main_database()

        actions = Counter()
        actions['merged'] = 0


        for n in count(skip):

            first = EpisodeUserState.view('episode_states/by_user_episode',
                    skip         = n,
                    include_docs = True,
                    limit        = 1,
                )
            first = list(first)
            if not first:
                break

            first = first[0]


            states = EpisodeUserState.view('episode_states/by_user_episode',
                    key          = [first.user, first.episode],
                    include_docs = True,
                )
            states = list(states)

            l1 = len(states)
            # we don't want to delete this one
            states.remove(first)

            assert len(states) == l1-1

            if states:
                updater = get_updater(states)

                obj_funs = [(first, updater)] + [(state, do_delete) for state in states]

                bulk_save_retry(db, obj_funs)

                merged = len(states)-1
                actions['merged'] += merged
                total -= merged

            status_str = ', '.join('%s: %d' % x for x in actions.items())
            progress(n+1, total, status_str)


def get_updater(states):

    actions = set()
    settings = dict()
    merged_ids = set()
    chapters = set()

    for state in states:
        actions.union(set(state.actions))
        settings.update(state.settings)
        merged_ids.union(set(state.merged_ids + [state._id]))
        chapters.union(set(state.chapters))

    return partial(do_update, list(actions), settings, list(merged_ids), list(chapters))


def do_update(actions, settings, merged_ids, chapters, state):
    state.add_actions(actions)
    # overwrite settings in old_state with state's settings
    state.settings = settings.update(state.settings or {})
    state.merged_ids = list(set(state.merged_ids + merged_ids))
    state.chapters = list(set(state.chapters + chapters))
    return state


def do_delete(state):
    # remove all attributes
    for attr in filter(lambda n: not n.startswith('_'), dir(state)):
        try:
            delattr(state, attr)
        except AttributeError:
            pass

    state._deleted = True
    return state
