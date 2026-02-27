"""Channel abstraction for multi-platform messaging."""

from openjarvis.channels._stubs import (
    BaseChannel,
    ChannelHandler,
    ChannelMessage,
    ChannelStatus,
)

# Trigger registration of built-in channels
try:
    import openjarvis.channels.telegram  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.discord_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.slack  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.webhook  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.email_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.whatsapp  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.signal_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.google_chat  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.irc_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.webchat  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.teams  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.matrix_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.mattermost  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.feishu  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.bluebubbles  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.whatsapp_baileys  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.line_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.viber_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.messenger_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.reddit_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.mastodon_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.xmpp_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.rocketchat_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.zulip_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.twitch_channel  # noqa: F401
except ImportError:
    pass

try:
    import openjarvis.channels.nostr_channel  # noqa: F401
except ImportError:
    pass

__all__ = [
    "BaseChannel",
    "ChannelHandler",
    "ChannelMessage",
    "ChannelStatus",
]
