#!/usr/bin/env python3
"""Installed Linux Home tile rename and icon round trip on an owned Xorg display."""
from contextlib import contextmanager
from io import BytesIO
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

from PIL import Image
from playwright.sync_api import expect, sync_playwright

from editor_lan_chat_x11 import NativeEditor, eventually, native_windows, ui

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'web'))
from v821_home_project_display import choose, picker, selected_identity
from v821_home_recent_edits import attach, editor, home, make_project, open_project, tile


class InstalledGtk(NativeEditor):
    def __init__(self, package, root, label):
        super().__init__(None, root / 'profile', package / 'content')
        self.package, self.root = package, root
        self.log = root / (label + '.log')

    def command(self, command, setup=False, **variables):
        env = dict(os.environ, CONFECTORY_HOME_STORAGE=str(self.profile),
                   CONFECTORY_ENTRY_STORAGE=str(self.profile), CONFECTORY_HOME_TRACE='1',
                   CONFECTORY_MCP_DIRECTORY=str(self.root / 'gtk-instances'), CONFECTORY_UI='native',
                   GSETTINGS_BACKEND='memory', **variables)
        for name in ('CONFECTORY_WEB_PROJECT', 'CONFECTORY_TEST_PUBLIC_CHAT_RELAY',
                     'CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK'):
            env.pop(name, None)
        return ['setsid', 'env', *(f'{key}={value}' for key, value in env.items()), *command]

    def menu(self, index):
        x, y, w, h = self.bounds(500 + index)
        ui.click(self.window, x + w // 2, y + h // 2, button=3)
        self.wait(lambda row: 441 in row['hits'][::5] and 442 in row['hits'][::5], 'Home tile context menu')

    def bounds(self, control):
        row = self.wait(lambda row: control in row['hits'][::5], f'Home control {control}')
        start = row['hits'][::5].index(control) * 5 + 1
        return row['hits'][start:start+4]

    def choose_image(self, path=None):
        self.click(444)
        title = b'Choose project icon'
        window = eventually(lambda: next(iter(native_windows(title)), None), 'GTK image chooser')
        self.wait(lambda row: row['nativePickerPending'], 'GTK chooser is active')
        if path is None:
            ui.key(window, 0xFF1B)
        else:
            ui.key(window, 'l', (0xFFE3,))
            ui.text(window, str(path))
            ui.key(window, 0xFF0D)
            if native_windows(title):
                ui.key(window, 0xFF0D)
        eventually(lambda: not native_windows(title), 'GTK image chooser dismissed')
        return self.wait(lambda row: row['screen'] == 'project-icon' and not row['nativePickerPending'],
                         'Home icon dialog resumes')

    def tile_pixels(self, index):
        x, y, _, _ = self.bounds(500 + index)
        screenshot = subprocess.check_output(['import', '-window', hex(self.window), 'png:-'])
        image = Image.open(BytesIO(screenshot)).convert('RGB')
        return image.getpixel((x-19, y+19)), image.getpixel((x-19, y+6))


@contextmanager
def gtk(package, root, label):
    app = InstalledGtk(package, root, label)
    try:
        app.launch(['/bin/sh', str(package / 'run')])
        app.wait(lambda row: row['screen'] == 'home' and row['model'].get('homeActivity'), 'GTK Home ready')
        yield app
        app.close()
    finally:
        if hasattr(app, 'child') and app.child.poll() is None:
            os.killpg(app.child.pid, signal.SIGTERM)
            app.child.wait(timeout=10)
        if hasattr(app, 'stream') and not app.stream.closed:
            app.stream.close()


def close_project(app):
    app.click(33)
    app.click(52)
    state = app.wait(lambda row: row['screen'] == 'home' or row['model'].get('closeRequest'), 'Close project')
    if state['screen'] != 'home':
        app.click(65)
    app.wait(lambda row: row['screen'] == 'home', 'Return to Home')


def assert_pixel(pixel, expected, tolerance=4):
    assert all(abs(a-b) <= tolerance for a, b in zip(pixel, expected)), (pixel, expected)


def workflow(package, root):
    (root / 'profile').mkdir()
    projects = [make_project(package, root, title)[0] for title in ('Alpha', 'Bravo')]
    listings = [{'path': str(project), 'title': project.parent.name,
                  'description': project.parent.name + ' details' } for project in projects]
    catalog = root / 'profile/projects.json'
    catalog.write_text(json.dumps(listings))
    first_source = root / 'source.png'
    Image.new('RGB', (32, 16), (160, 70, 200)).save(first_source)

    def snapshot():
        return catalog.read_bytes(), catalog.stat().st_mtime_ns

    def unchanged(before):
        assert snapshot() == before

    with gtk(package, root, 'gtk-first') as app:
        identities = []
        for index, project in enumerate(projects):
            app.click(100 + 3*index)
            selected = app.wait(lambda row: row['screen'] == 'project', 'Original project opens')['model']['selected']
            assert selected['path'] == str(project)
            identities.append(selected['projectId'])
            close_project(app)
        assert identities[0] != identities[1]
        original_files = {path: path.read_bytes() for project in projects
                          for path in project.parent.rglob('*') if path.is_file()}
        original_image = first_source.read_bytes()
        before = snapshot()

        app.menu(0)
        app.click(441)
        app.fill(431, 'Unapplied title')
        app.click(440)
        app.click(430)
        unchanged(before)

        app.menu(0)
        app.click(441)
        app.fill(431, 'Alpha Renamed')
        app.click(434)
        app.wait(lambda row: not row['job'] and row['model']['cards'][0]['title'] == 'Alpha Renamed', 'Name saved')
        app.click(430)
        listings[0]['title'] = 'Alpha Renamed'
        assert json.loads(catalog.read_bytes()) == listings
        before_icon = snapshot()

        app.menu(0)
        app.click(442)
        app.choose_image()
        unchanged(before_icon)
        app.choose_image(first_source)
        app.wait(lambda row: row['message'].startswith('Image selected'), 'PNG prepared')
        unchanged(before_icon)
        app.click(446)
        unchanged(before_icon)

        app.menu(0)
        app.click(442)
        too_large = root / 'oversize.png'
        with too_large.open('wb') as stream:
            stream.write(original_image)
            stream.truncate(5_000_001)
        app.choose_image(too_large)
        app.wait(lambda row: row['message'].startswith('Could not read the image'), 'Reject image over the size limit')
        assert 445 not in app.state()['hits'][::5]
        unchanged(before_icon)

        # Exercise both other accepted input types without applying either preview.
        for suffix in ('jpg', 'webp'):
            alternate = root / ('alternate.' + suffix)
            Image.new('RGB', (13, 31), (50, 90, 140)).save(alternate)
            app.choose_image(alternate)
            app.wait(lambda row: row['message'].startswith('Image selected'), f'{suffix} prepared')
            unchanged(before_icon)
        app.choose_image(first_source)
        app.click(445)
        app.wait(lambda row: row['screen'] == 'home' and row['message'] == 'Project icon saved locally.', 'Icon applied')
        saved_icon = json.loads(catalog.read_bytes())[0]['icon']
        listings[0]['icon'] = saved_icon
        assert json.loads(catalog.read_bytes()) == listings
        center, padding = app.tile_pixels(0)
        assert_pixel(center, (160, 70, 200))
        assert_pixel(padding, (0x21, 0x36, 0x44))
        assert first_source.read_bytes() == original_image

    Image.new('RGB', (32, 16), (35, 200, 77)).save(first_source)
    with gtk(package, root, 'gtk-cold') as app:
        center, padding = app.tile_pixels(0)
        assert_pixel(center, (160, 70, 200))
        assert_pixel(padding, (0x21, 0x36, 0x44))
        for index, (listing, identity) in enumerate(zip(listings, identities)):
            app.click(100 + index*3)
            selected = app.wait(lambda row: row['screen'] == 'project', 'Cold-open exact Home tile')['model']['selected']
            assert (selected['title'], selected['projectId'], selected['path']) == (listing['title'], identity, listing['path'])
            close_project(app)

    browser_image = root / 'browser.png'
    Image.new('RGB', (32, 16), (40, 145, 220)).save(browser_image)
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            with editor(package, root, 'chromium') as url:
                page, errors = attach(browser, url)
                icon = tile(page, 'Alpha Renamed').locator('.project-icon img')
                expect(icon).to_have_attribute('src', saved_icon)
                assert icon.evaluate('async img => { await img.decode(); return img.naturalWidth; }') == 128
                expect(tile(page, 'Bravo').locator('.project-icon img')).to_have_count(0)
                for listing, identity in zip(listings, identities):
                    open_project(page, listing['title'])
                    assert selected_identity(url)[0] == identity
                    home(page)
                dialog = picker(page, 'Alpha Renamed')
                choose(page, dialog, str(browser_image))
                preview = dialog.locator('.object-icon-preview img')
                expect(preview).not_to_have_attribute('src', saved_icon)
                listings[0]['icon'] = preview.get_attribute('src')
                dialog.get_by_role('button', name='적용', exact=True).click()
                expect(icon).to_have_attribute('src', listings[0]['icon'])
                eventually(lambda: json.loads(catalog.read_bytes()) == listings, 'Chromium icon persisted')
                assert not errors, errors
                page.close()

    with gtk(package, root, 'gtk-after-browser') as app:
        center, padding = app.tile_pixels(0)
        assert_pixel(center, (40, 145, 220))
        assert_pixel(padding, (0x21, 0x36, 0x44))

    assert json.loads(catalog.read_bytes()) == listings
    assert all(path.read_bytes() == original for path, original in original_files.items())
    print('PASS installed GTK rename, real image chooser, cancellation, bounded images, cold identities and GTK/Chromium icon interchange')


if __name__ == '__main__':
    expect.set_options(timeout=45000)
    package = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix='gtk-home-project-display-') as path:
        workflow(package, Path(path))
