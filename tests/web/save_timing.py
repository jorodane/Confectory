"""Actual click, new success mutation and command-enabled frame, not assertion polling."""

def arm_save_timing(button):
    button.evaluate("""el => {
      globalThis.__saveTiming = null;
      el.addEventListener('click', () => {
        const start = performance.now(), timing = globalThis.__saveTiming = {start, success: null, ready: null};
        const status = document.querySelector('#status');
        let sawDisabled = false;
        // The preceding save may still display the same text. Only a new
        // status mutation after this click counts as this save's success.
        const observer = new MutationObserver(() => {
          if (status.textContent.trim() === '저장했습니다.' && timing.success === null) timing.success = performance.now() - start;
        });
        observer.observe(status, {childList: true, characterData: true, subtree: true});
        const tick = () => {
          if (globalThis.__saveTiming !== timing) { observer.disconnect(); return; }
          const menu = document.querySelector('#project-menu');
          if (menu?.disabled) sawDisabled = true;
          if (sawDisabled && timing.success !== null && menu && !menu.disabled) { timing.ready = performance.now() - start; observer.disconnect(); return; }
          if (performance.now() - start < 120000) requestAnimationFrame(tick); else observer.disconnect();
        };
        requestAnimationFrame(tick);
      }, {capture: true, once: true});
    }""")

def actual_save_timing(page):
    page.wait_for_function("() => globalThis.__saveTiming?.ready != null", timeout=120000)
    return page.evaluate("globalThis.__saveTiming")
