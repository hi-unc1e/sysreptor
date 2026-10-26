# Dokploy deployment

This fork has an isolated deployment branch, `codex/dokploy`.
Pushes to this branch trigger the GitHub App webhook and a native Dokploy
Application deployment. The upstream `main` branch is unchanged.

## Build and runtime

- Build type: root `Dockerfile`, context `.`; no local Mac builds.
- Build server: Singapore, one concurrent build.
- Registry: the configured private Aliyun registry.
- Runtime server: Hong Kong; internal HTTP port 8000.
- Public URL: https://sysreptor.apps.unc.la
- Health check: `/api/public/utils/healthcheck/`.

The PostgreSQL and Redis dependencies run on a dedicated private network,
without host ports. `/data` and PostgreSQL data use persistent volumes.
Database credentials, the Django secret, and encryption keys belong only in
Dokploy environment settings and the private operations backup, never Git.
Keep encryption keys with the database and uploaded-file backups: restoring
only the data without its keys is insufficient.

## Deploy a change

1. Commit and push to `codex/dokploy`.
2. Open the SysReptor Application in Dokploy, then Deployments.
3. Match the deployment commit SHA to the pushed commit and check the build log.
4. Verify the health check and log in to the application. A successful build
   alone does not establish application health or report-rendering correctness.

Changing the production branch requires changing the GitHub provider branch
in Dokploy. Do not enable a second deployment pipeline for the same instance.
The GitHub App needs repository contents/metadata read access and push events;
it does not need code-write or personal-email permissions.
