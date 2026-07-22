import json
import time
import asyncio
import logging
from playwright.async_api import Page

logger = logging.getLogger("NetLogger")

WEBGL_HOOK = r"""
(() => {
  // Hook HTMLImageElement.src assignment
  try {
    const ImgProto = HTMLImageElement.prototype;
    const setSrc = Object.getOwnPropertyDescriptor(ImgProto, 'src')?.set;
    Object.defineProperty(ImgProto, 'src', {
      set: function(v) {
        console.info(JSON.stringify({type:'image-src-set', src:v}));
        if (setSrc) setSrc.call(this, v);
      }
    });
  } catch (e) {}

  // Hook createImageBitmap
  try {
    const originalCreateImageBitmap = window.createImageBitmap;
    window.createImageBitmap = function() {
      try { console.info(JSON.stringify({type:'createImageBitmap', args: Array.from(arguments)})); } catch(e){}
      return originalCreateImageBitmap.apply(this, arguments);
    };
  } catch (e) {}

  // Hook WebGL texImage2D (both WebGLRenderingContext and WebGL2RenderingContext)
  function hookTex(proto) {
    if (!proto || !proto.texImage2D) return;
    const orig = proto.texImage2D;
    proto.texImage2D = function() {
      try {
        console.info(JSON.stringify({type:'webgl-texImage2D', args: Array.from(arguments).map(a=>{
          try { return a && a.src ? a.src : (a && a.url) ? a.url : String(a).slice(0,100); } catch(e){ return typeof a; }
        })}));
      } catch (e){}
      return orig.apply(this, arguments);
    };
  }
  hookTex(WebGLRenderingContext && WebGLRenderingContext.prototype);
  hookTex(WebGL2RenderingContext && WebGL2RenderingContext.prototype);
})();
"""

async def attach_network_logger(page: Page, out_path: str = "netlog.ndjson"):
    """
    Podłącza logowanie request/response/console i wstrzykuje hooki WebGL/Image.
    Zapisuje linie JSON do out_path (NDJSON).
    """
    f = open(out_path, "a", encoding="utf-8")

    def _write(obj):
        try:
            f.write(json.dumps({"ts": time.time(), **obj}, default=str) + "\n")
            f.flush()
        except Exception:
            logger.exception("Błąd podczas zapisu logu sieciowego")

    def on_request(request):
        try:
            _write({
                "event": "request",
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "headers": {k:v for k,v in request.headers.items() if k.lower() not in ('cookie','authorization')},
            })
        except Exception:
            logger.exception("on_request error")

    async def on_response(response):
        try:
            req = response.request
            info = {
                "event": "response",
                "url": response.url,
                "status": response.status,
                "resource_type": req.resource_type,
                "headers": {k:v for k,v in response.headers.items() if k.lower() not in ('set-cookie',)},
            }
            # opcjonalnie logować nagłówek content-type
            ct = response.headers.get("content-type")
            if ct:
                info["content_type"] = ct
            _write(info)
        except Exception:
            logger.exception("on_response error")

    def on_request_failed(request):
        try:
            _write({
                "event": "requestfailed",
                "url": request.url,
                "resource_type": request.resource_type,
                "failure": request.failure
            })
        except Exception:
            logger.exception("on_request_failed error")

    def on_console(msg):
        try:
            # Playwright ConsoleMessage bezpiecznie przekonwertować
            _write({
                "event": "console",
                "type": msg.type,
                "text": msg.text,
            })
        except Exception:
            logger.exception("on_console error")

    # attach handlers
    page.on("request", on_request)
    page.on("response", lambda r: asyncio.create_task(on_response(r)))
    page.on("requestfailed", on_request_failed)
    page.on("console", on_console)

    # Inject hook scripts as early as possible
    await page.add_init_script(WEBGL_HOOK)

    # helper: snapshot DOM images/backgrounds after load
    async def snapshot_dom(tag="dom_snapshot"):
        try:
            dom_data = await page.evaluate("""
            () => {
              const imgs = Array.from(document.querySelectorAll('img')).map(i=>({
                src: i.getAttribute('src'),
                currentSrc: i.currentSrc,
                srcset: i.getAttribute('srcset'),
                data: {...i.dataset},
                loading: i.loading || null,
                complete: i.complete || null,
                naturalWidth: i.naturalWidth || 0,
                naturalHeight: i.naturalHeight || 0,
              }));
              const bg = Array.from(document.querySelectorAll('*')).map(el=>{
                const s = window.getComputedStyle(el).getPropertyValue('background-image');
                return s && s !== 'none' ? {tag: el.tagName, bg: s, selector: el.tagName} : null;
              }).filter(Boolean);
              const canvases = Array.from(document.querySelectorAll('canvas')).map(c=>({w:c.width, h:c.height}));
              return {imgs, bg, canvases, url: location.href};
            }
            """)
            _write({"event": tag, "data": dom_data})
        except Exception:
            logger.exception("snapshot_dom error")

    # zwróć funkcję snapshot i zamknięcie pliku
    async def close():
        try:
            page.off("request", on_request)
            page.off("response", lambda r: asyncio.create_task(on_response(r)))
            page.off("requestfailed", on_request_failed)
            page.off("console", on_console)
            f.close()
        except Exception:
            logger.exception("error closing netlogger")
    return snapshot_dom, close
