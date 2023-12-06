# Demo: SSO Logon to Control Room

This demo robot logs onto Control Room using SSO and MFA via OTP. Once logged on it starts a demo process and waits for confirmation that it started.

## Pre-requisites

* A Control Room with Okta SSO and MFA enabled
* A user with SSO enabled in Control Room

## Vault and Storage Configuration

This demo uses the following vault and storage configuration:

* Vault: `sso_account` with the following keys:
    * `email`: The username of the user to log on with
    * `password`: The password of the user to log on with
    * `mfa_secret_key`: The secret key for MFA
* Storage (all optional):
    * `CONTROL_ROOM_URL`: The URL of the Control Room to log on to. Defaults to `https://cloud.robocorp.com/`. If you set this to a URL with a custom subdomain, you do not need to set `CONTROL_ROOM_SUBDOMAIN`.
    * `CONTROL_ROOM_SUBDOMAIN`: The subdomain of the Control Room to log on to. Defaults to `eu1-acme`. If you set this to a custom subdomain, you should not set `CONTROL_ROOM_URL`.
    * `CONTROL_ROOM_PROCESS_NAME`: The name of the process to start. Defaults to `Demo`.