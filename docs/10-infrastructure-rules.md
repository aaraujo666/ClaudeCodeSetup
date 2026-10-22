# 10. Infrastructure rules: standing rules for anything new

A homelab, or any small fleet, rots in the same way: something gets created in a hurry
and never recorded, and six months later nobody knows what it is, whether it is
reachable, or what time it thinks it is. The cure is a short list of things that happen
in the *same pass* that creates the thing, without being asked.

When a host, VM, container or service comes into existence, three things happen.

## 1. Register it, and prove it with a real command

Every VM or host goes into the inventory that the infrastructure MCP server reads. Every
container goes into the compose stack on the docker host, as a service in a
version-controlled file, never as a loose `docker run` that exists only in someone's shell
history.

Then prove the registration with a command that exercises the path you will actually use:
an SSH command that returns output, not a ping. A ping or a port check only tells you the
port is open. A real command tells you the key works, the user exists, the shell starts and
the host is the one you think it is.

```text
inventory add  name=build-runner-2  address=<ADDRESS>  user=ops  key=~/.ssh/<KEY>
config_reload
ssh_exec build-runner-2 "hostname && uname -r"
-> build-runner-2
-> 6.1.0-18-amd64
```

Reachability checked by a port probe only is "probably". Reachability checked by a real
command is "yes".

## 2. A browser UI gets a tile on the start page

If the service has a web interface, it gets a tile on the start page I use as my browser's
home. Back the page up first, edit it, and check the tile resolves. A service you cannot
find from the start page is a service you will forget exists. The page is a plain static
file on the hypervisor, read and edited over SSH, because a fetch-based tool cannot read
it.

## 3. Set the timezone

Timezone defaults differ between images, and a host in the wrong zone produces logs and
cron schedules that disagree with each other in ways that take an afternoon to see. The
rule is one timezone for the fleet, set at provisioning time:

- The provisioning tools set it by default.
- Data is *stored* in UTC regardless; the host's local zone is for logs and cron.
- Verify by hand on anything provisioned another way.
- Images without timezone data need the zoneinfo files mounted in.

**CI enforces it.** The compose stack's pipeline has a `tz-check` job that fails any
service missing a `TZ` setting:

```yaml
tz-check:
  stage: lint
  script:
    - |
      missing=$(python3 - <<'PY'
      import sys, yaml
      doc = yaml.safe_load(open("compose.yaml"))
      bad = []
      for name, svc in (doc.get("services") or {}).items():
          env = svc.get("environment") or {}
          flat = env if isinstance(env, list) else [f"{k}={v}" for k, v in env.items()]
          if not any(str(e).startswith("TZ=") for e in flat):
              bad.append(name)
      print(" ".join(bad))
      PY
      )
      if [ -n "$missing" ]; then echo "services missing TZ: $missing"; exit 1; fi
```

A rule that CI fails is a rule that holds. The same service, registered, tiled and
timezoned, is a different animal from one that merely runs.

## Other standing rules in the same spirit

- **Capacity and placement.** Anything to install or spin up goes on the docker host, not
  on a workstation. It has the CPUs, the RAM and the storage.
- **A scratch VM is free to break.** One designated VM has a standing authorisation to be
  destroyed and rebuilt, which makes provisioning experiments cheap. Every other VM is
  ask-first.
- **Alerts reach a phone.** A metrics stack pushes alerts through a notification service
  to a phone. You cannot alert on the host that runs the alerting, so know that gap.
- **Time sync is a source and a check.** One machine is the LAN's time source. Do not
  trust the OS's own "synchronised" flag; check the exporter metric that reports it.
- **Backups pull over SSH.** The backup host pulls; the things being backed up hold no
  credentials for it.
- **Check what "running" means.** A VM listed as running is not necessarily healthy.
  Record the verification command beside the host.

All of these were learned by being wrong first, and each is a memory entry. They are
written down as rules because a rule applied at creation time costs minutes, and the same
thing applied after the fact costs an afternoon.

Next: [11 Verification](11-verification.md)
