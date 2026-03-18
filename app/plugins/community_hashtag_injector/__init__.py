from app.activitypub.util import find_hashtag_or_create
from app.plugins.hooks import hook

# Hard-code community IDs to the hashtags that should be added before ActivityPub federation.
# Example:
# COMMUNITY_HASHTAG_MAP = {
#     123: ["tokyo", "localnews"],
#     456: ["eventinfo"],
# }
COMMUNITY_HASHTAG_MAP = {
    11: ["karasu_test"],
    17: ["precure_fun"],       #プリキュア
    67: ["PieFed"],            #PieFed JP
    112: ["DQウォーク", "DQW"]  #DQW
}

def apply_community_hashtags(tag_context):
    if not isinstance(tag_context, dict):
        return tag_context

    community = tag_context.get('community')
    if community is None:
        post = tag_context.get('post')
        community = getattr(post, 'community', None)

    if community is None or not community.is_local():
        return tag_context

    configured_hashtags = COMMUNITY_HASHTAG_MAP.get(community.id, [])
    if not configured_hashtags:
        return tag_context

    tags = list(tag_context.get('tags') or [])
    existing_names = {tag.name for tag in tags if getattr(tag, 'name', None)}

    for hashtag in configured_hashtags:
        tag = find_hashtag_or_create(hashtag)
        if tag and tag.name not in existing_names:
            tags.append(tag)
            existing_names.add(tag.name)

    tag_context['tags'] = tags
    return tag_context


@hook('before_post_federate')
def add_community_hashtags_before_post_federate(tag_context, **kwargs):
    return apply_community_hashtags(tag_context)


def plugin_info():
    return {
        'name': 'Community Hashtag Injector',
        'version': '1.0.0',
        'description': 'コミュニティに応じたハッシュタグを自動で付与する',
        'license': 'AGPL-3.0',
        'source_url': 'https://github.com/karasugawasu/pyfedi/tree/main/app/plugins/community_hashtag_injector',
        'author': 'karasugawasu',
    }
