import logging
from typing import Optional
from services.host_core.tools.impl.navigation import NavigationTools
import hubscape_adk

logger = logging.getLogger(__name__)

async def resolve_navigation(
    nav_type: str,
    url: Optional[str] = None,
    target_hub: Optional[str] = None,
    reason: str = "User requested navigation."
) -> dict:
    """Directly executes a navigation action: opens an external link in a new tab, switches the user to a different hub, or ends the current call.

    Args:
        nav_type: The type of navigation: 'link', 'switch', 'end_call'
        url: The external URL to open if nav_type is 'link'
        target_hub: The target hub name or ID if nav_type is 'switch'
        reason: The reason for ending the call or switching hub
    """
    context = hubscape_adk.get_context()
    logger.info(f"[navigation_agent] Resolving navigation: type={nav_type}, url={url}, target={target_hub}")

    # Build a minimal context dict NavigationTools expects
    nav_context = {
        "userId": context.auth.get_user_id() if context.auth else None,
        "latestSearchResults": context.latest_search_results,
    }

    if nav_type == 'link':
        if not url:
            return {
                "status": "error",
                "message": "I could not open the link because the destination URL was missing."
            }
        result = await NavigationTools.open_external_link({"url": url}, nav_context)
        return {
            "status": "success",
            "message": f"Opening {url} in a new tab for you.",
            "system_action": result.get("system_action")
        }

    elif nav_type == 'switch':
        if not target_hub:
            return {
                "status": "error",
                "message": "I could not switch hubs because the target hub was not provided."
            }
        result = await NavigationTools.switch_hub({"hubId": target_hub, "reason": reason}, nav_context)
        return {
            "status": "success",
            "message": result.get("result", "Switching hub context."),
            "system_action": result.get("system_action")
        }

    elif nav_type == 'end_call':
        result = await NavigationTools.end_call({"reason": reason}, nav_context)
        return {
            "status": "success",
            "message": result.get("result", "Ending the call."),
            "system_action": result.get("system_action")
        }

    else:
        return {
            "status": "error",
            "message": f"I did not recognise the navigation type '{nav_type}'."
        }
