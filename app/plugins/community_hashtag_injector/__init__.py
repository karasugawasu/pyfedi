from flask import Blueprint, current_app, jsonify

from app.activitypub.util import find_hashtag_or_create
from app.models import Community
from app.plugins.hooks import hook

bp = Blueprint('community_hashtag_injector', __name__)

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

def configured_communities_by_id():
    configured_ids = list(COMMUNITY_HASHTAG_MAP.keys())
    if not configured_ids:
        return {}

    communities = Community.query.filter(Community.id.in_(configured_ids)).all()
    return {community.id: community for community in communities}


def community_acct(community):
    if community is None:
        return None
    if community.ap_id:
        return community.ap_id.lower()
    return f"{community.name.lower()}@{current_app.config['SERVER_NAME']}"


def community_hashtag_map_payload():
    communities_by_id = configured_communities_by_id()
    communities = []

    for community_id, hashtags in COMMUNITY_HASHTAG_MAP.items():
        community = communities_by_id.get(community_id)
        if community is None:
            continue
        communities.append({
            'id': community_id,
            'acct': community_acct(community),
            'title': getattr(community, 'title', None),
            'hashtags': hashtags,
        })

    return {
        'communities': communities,
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

@bp.get('/plugins/community-hashtag-map.json')
def get_community_hashtag_map():
    return jsonify(community_hashtag_map_payload())

@hook('before_post_federate')
def add_community_hashtags_before_post_federate(tag_context, **kwargs):
    return apply_community_hashtags(tag_context)

def init_app(app):
    app.register_blueprint(bp)

def plugin_info():
    return {
        'name': 'Community Hashtag Injector',
        'version': '1.0.0',
        'description': 'コミュニティに応じたハッシュタグを自動で付与する',
        'license': 'AGPL-3.0',
        'source_url': 'https://github.com/karasugawasu/pyfedi/tree/main/app/plugins/community_hashtag_injector',
        'author': 'karasugawasu',
    }
