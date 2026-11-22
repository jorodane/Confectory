"""Hold one real browser Run observation for the selected test window."""


def hold_run_read(page, key, error=None):
    prefix = "run:instance:"
    assert key.startswith(prefix), key
    page.evaluate(
        """({view, error}) => {
          const receive = globalThis.fetch;
          const gate = {held: false, release: null};
          globalThis.__runReadGate = gate;
          globalThis.fetch = async (...args) => {
            const response = await receive(...args);
            if (gate.held) return response;
            let request;
            try { request = JSON.parse(args[1]?.body || '{}'); }
            catch { return response; }
            if (request.op !== 'observe' || request.endpoint !== 'runWindowRead' ||
                request.input?.view !== view) return response;
            const packet = await response.clone().json();
            if (gate.held || !packet.ok || packet.result?.view !== view ||
                packet.result.state !== 'running') return response;
            await new Promise(resolve => {
              gate.release = resolve;
              gate.held = true;
            });
            if (!error) return response;
            delete packet.result;
            packet.ok = false;
            packet.error = {code: error};
            return new Response(JSON.stringify(packet), {
              status: 200, headers: {'Content-Type': 'application/json'}
            });
          };
        }""",
        {"view": key.removeprefix(prefix), "error": error},
    )
    page.wait_for_function("() => globalThis.__runReadGate.held")


def release_run_read(page):
    page.evaluate("() => globalThis.__runReadGate?.release?.()")
