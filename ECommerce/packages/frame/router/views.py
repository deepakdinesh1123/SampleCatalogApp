from django.views.generic import View

from ..decorator import apply_frame_routing


class FrameRouterView(View):
    """
    View for frame routing.

    Redirects users based on frame configuration.
    """

    @classmethod
    def as_view(cls):
        return apply_frame_routing(super(FrameRouterView, cls).as_view())
