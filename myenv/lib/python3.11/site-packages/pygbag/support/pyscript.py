# ======================================================
# emulate pyodide display() cmd
# TODO: fixme target
async def async_display(obj, target=None, **kw):
    filename = aio.filelike.mktemp(".png")
    target = kw.pop("target", None)
    x = kw.pop("x", 0)
    y = kw.pop("y", 0)
    dpi = kw.setdefault("dpi", 72)
    if repr(type(obj)).find("matplotlib.figure.Figure") > 0:
        # print(f"matplotlib figure {platform.is_browser=}")
        if platform.is_browser:
            # Agg is not avail, save to svg only option.
            obj.canvas.draw()
            tmp = f"{filename}.svg"
            obj.savefig(tmp, format="svg", **kw)
            await platform.jsiter(platform.window.svg.render(tmp, filename))
        else:
            # desktop matplotlib can save to any format
            obj.canvas.draw()
            obj.savefig(filename, format="png", **kw)

    if target in [None, "pygame"]:
        import pygame

        screen = shell.pg_init()
        screen.fill((0, 0, 0))
        screen.blit(pygame.image.load(filename), (x, y))
        pygame.display.update()


import js


def display(*values, target=None, append=True):
    print(f"{values} {target=} {append=}")
