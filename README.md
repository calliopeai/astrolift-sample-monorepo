# Astrolift managed CI monorepo fixture

Two independent HTTP services exercise image build, publication and deployment
for separately registered apps in one source repository. Each service listens
on port 8080, serves `/` and `/health`, and returns a distinct
`X-Astrolift-Fixture-App` header. HEAD requests can verify identity without
retaining response bodies. No credentials or external services are required by
the applications.

## Per-app build inputs

Save these inputs on the corresponding registration; manifest location does
not implicitly select the app's build context. `dockerfilePath` is relative to
`buildContext`, while `buildContext` is relative to the repository root.

| App | Manifest path | Build context | Dockerfile path | Identity header |
| --- | --- | --- | --- | --- |
| API | `apps/api/astrolift.toml` | `.` | `apps/api/Dockerfile` | `mono-api` |
| Web | `apps/web/astrolift.toml` | `apps/web` | `Dockerfile` | `mono-web` |

Register each manifest independently with explicit name/slug and
`buildMode = ci_pushed`. Use isolated fixture registrations with distinct ECR
repositories and environments; retain the existing manifest/workload shape.
Both Dockerfiles run as UID/GID 10001 and need no pip install or build secrets.
The checked-in `image_ref` values are existing sample defaults, not evidence
that the newly built image was deployed. Confirm each actual running digest
against its own commit-tagged ECR image.

## Native check

```sh
python3 scripts/check_fixture.py
```

This launches both actual service entrypoints on temporary local ports, checks
health, independent identity headers, HEAD responses and unknown-route 404s,
then stops both processes. It invokes neither Docker nor a platform API.

## Actual CI acceptance

After the compatible platform release, use supported CI setup to push each
fixture app's scoped secrets and synchronize its GUID-owned workflow. Merge
any required review PR before testing a new source commit. Each real workflow
must build with the inputs above, push its own `<repository>:<commit-sha>`
image, and only then notify Astrolift. Record both GitHub run IDs, immutable
ECR digests and successful exact-app/environment deployments for the same
fresh commit. Compare the harmless identity headers to the selected app.

Native checks do not prove a container build, GitHub Actions execution, image
push or Kubernetes deployment. Those remain separate acceptance steps. No
managed workflows, deployment secrets or cloud configuration are checked in.
