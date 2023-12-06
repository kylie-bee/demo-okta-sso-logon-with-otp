import os
import pyotp
from robocorp import browser, vault, log, storage
from robocorp.tasks import task

DEFAULT_URL = "https://cloud.robocorp.com/"
DEFAULT_SUBDOMAIN = "eu1-acme"
DEFAULT_PROCESS_NAME = "Demo"


@task
def demo_sso_logon_to_control_room():
    """Logs into Control Room and starts a demo process."""
    credentials = vault.get_secret("sso_account")
    otp = pyotp.TOTP(credentials["mfa_secret_key"])
    url = get_url()
    subdomain = get_subdomain()
    demo_process_name = get_process_name()
    log.info(f"Logging into Control Room at {url} using {subdomain}.")
    page = logon_to_control_room(url, subdomain, credentials, otp)
    log.info(f"Starting the {demo_process_name} process.")
    start_process_by_name(page, demo_process_name)
    log.info("SSO login demo finished.")


def get_url():
    """Returns the URL to the Control Room based on
    the value of the CONTROL_ROOM_URL text storage asset.

    If the asset is not found, an environment variable
    with the same name is used.

    Finally, if the environment variable is not found,
    the default value of https://cloud.robocorp.com/orgrobocorp/demo
    is used.
    """
    try:
        return storage.get_text("CONTROL_ROOM_URL")
    except:
        try:
            return os.environ["CONTROL_ROOM_URL"]
        except KeyError:
            return DEFAULT_URL


def get_subdomain():
    """Returns the subdomain to use for the SSO login
    based on the value of the CONTROL_ROOM_SUBDOMAIN text storage asset.

    If the asset is not found, an environment variable
    with the same name is used.

    Finally, if the environment variable is not found,
    the default value of orgrobocorp is used.
    """
    try:
        return storage.get_text("CONTROL_ROOM_SUBDOMAIN")
    except:
        try:
            return os.environ["CONTROL_ROOM_SUBDOMAIN"]
        except KeyError:
            return DEFAULT_SUBDOMAIN


def get_process_name():
    """Returns the name of the process to start
    based on the value of the CONTROL_ROOM_PROCESS_NAME text storage asset.

    If the asset is not found, an environment variable
    with the same name is used.

    Finally, if the environment variable is not found,
    the default value of Demo is used.
    """
    try:
        return storage.get_text("CONTROL_ROOM_PROCESS_NAME")
    except:
        try:
            return os.environ["CONTROL_ROOM_PROCESS_NAME"]
        except KeyError:
            return DEFAULT_PROCESS_NAME


def logon_to_control_room(
    url: str, subdomain: str, credentials: vault.SecretContainer, otp: pyotp.TOTP
) -> browser.Page:
    """Logs into Control Room and starts a demo process.

    Returns the logged on page.
    """
    page = browser.page()
    page.goto(url)
    sign_on_button = page.locator("xpath=//span[contains(.,'Sign in with SSO')]")
    okta_sign_in_button = page.locator("id=okta-signin-submit")
    sign_on_button.or_(okta_sign_in_button).wait_for(timeout=60000)
    if sign_on_button.is_visible():
        sign_on_button.click()
        page.fill("xpath=//*[@name='realm']", subdomain)
        page.click("xpath=//span[contains(.,'Continue')]")
    page.fill("id=okta-signin-username", credentials["email"])
    page.fill("id=okta-signin-password", credentials["password"])
    okta_sign_in_button.click()
    page.fill("xpath=//*[@name='answer']", otp.now())
    page.click("xpath=//input[@value='Verify']")
    page.wait_for_selector("xpath=//h1[contains(.,'Processes')]")

    return page


def start_process_by_name(page: browser.Page, name: str) -> None:
    """Starts a process within the Control Room by name."""
    if not page.url.endswith("/processes"):
        url_parts = page.url.split("/")
        organization = url_parts[3]
        workspace = url_parts[4]
        processes_url = f"https://{url_parts[2]}/{organization}/{workspace}/processes"
        page.goto(processes_url)
    page.click(f"xpath=//table//a[contains(.,'{name}')]")
    page.click("id=process__run-options")
    page.get_by_role("menuitem", name="Run", exact=True).click()
    page.wait_for_selector(
        "xpath=//p[contains(.,'Process Run started succesfully')]",
        timeout=60000,
    )
