import os.path
from unittest import mock

import kintro.decisions
import kintro.plex

import pytest


@pytest.fixture()
def plex_server(mocker):
    return None


@pytest.fixture()
def debug_mode():
    return False


@pytest.fixture()
def logger():
    class FakeLogger:
        def __init__(self):
            self.infos = []
            self.warnings = []
            self.debugs = []
            self.exceptions = []

        def info(self, *args, **kwargs):
            self.infos.append((args, kwargs))
            return None

        def warning(self, *args, **kwargs):
            self.warnings.append((args, kwargs))
            return None

        def debug(self, *args, **kwargs):
            self.debugs.append((args, kwargs))
            return None

        def exception(self, *args, **kwargs):
            self.exceptions.append((args, kwargs))
            return None

    return FakeLogger()


@pytest.fixture()
def app_obj(plex_server, logger, debug_mode):
    return {
        "debug": debug_mode,
        "plex": plex_server,
        "logger": logger,
    }


def describe_to_analyze():
    def force_analyze_true_exclusive(app_obj):
        assert kintro.plex.Analyze.ForceAnalyze == kintro.plex.to_analyze(
            app_obj,
            force_analyze=True,
            analyze_if_intro_missing=False,
        )

    def analyze_if_missing_true_exclusive(app_obj):
        assert kintro.plex.Analyze.AnalyzeIfIntroMissing == kintro.plex.to_analyze(
            app_obj,
            force_analyze=False,
            analyze_if_intro_missing=True,
        )

    def force_analyze_overrides_analyze_if_intro_missing(app_obj):
        assert kintro.plex.Analyze.ForceAnalyze == kintro.plex.to_analyze(
            app_obj,
            force_analyze=True,
            analyze_if_intro_missing=True,
        )

    def no_analyze(app_obj):
        assert kintro.plex.Analyze.NoAnalyze == kintro.plex.to_analyze(
            app_obj,
            force_analyze=False,
            analyze_if_intro_missing=False,
        )


@pytest.fixture()
def mocked_pbar():
    return mock.MagicMock()


class FakeMarker:
    def __init__(self, marker_type, start, end):
        self.type = marker_type
        self.start = start
        self.end = end


def describe_handle_episode():
    @pytest.fixture()
    def episodefn():
        def inner(has_intro_marker, markers=None, locations=None):
            patched = mock.MagicMock()
            patched.hasIntroMarker = has_intro_marker
            patched.markers = markers if markers is not None else []
            patched.locations = locations if locations is not None else []
            return patched

        return inner

    @pytest.mark.parametrize(
        "has_intro_marker, markers",
        [
            (False, None),
            (False, []),
            (True, []),
            (True, [FakeMarker("outro", 100, 2000)]),
        ],
    )
    def episode_no_intro_marker_detected(mocked_pbar, app_obj, episodefn, has_intro_marker, markers):
        episode = episodefn(has_intro_marker, markers)
        assert [] == kintro.plex.handle_episode(
            app_obj=app_obj,
            episode=episode,
            edit=kintro.decisions.DECISION_TYPES.cut,
            find_path=None,
            replace_path=None,
            dry_run=False,
            pbar=mocked_pbar,
            should_analyze=kintro.plex.Analyze.NoAnalyze,
        )
        mocked_pbar.update.assert_called_once_with()
        assert any("No intro markers found" in k[0][0] for k in app_obj["logger"].infos)

    @pytest.mark.parametrize(
        "markers, locations",
        [
            ([FakeMarker("intro", 1000, 4000)], ["path_to.mkv"]),
            ([FakeMarker("intro", 2000, 6000)], ["path_to.mkv", "another/path_to.mkv"]),
            (
                [FakeMarker("intro", 2000, 6000), FakeMarker("outro", 50000, 100000)],
                ["path_to.mkv", "another/path_to.mkv"],
            ),
            pytest.param(
                [FakeMarker("intro", 2000, 6000), FakeMarker("intro", 50000, 100000)],
                ["path_to.mkv", "another/path_to.mkv"],
                marks=pytest.mark.xfail(reason="Currently each write overwrites see #49"),
            ),
        ],
        ids=(
            "one_intro_marker-one-location",
            "one_intro_marker-two-locations",
            "one_intro_marker+one_outro_marker-two-locations",
            "two_intro_markers-two-locations",
        ),
    )
    def episode_intro_marker_detected(mocked_pbar, app_obj, episodefn, markers, locations):
        episode = episodefn(True, markers, locations)
        expected_files = [os.path.splitext(file)[0] + ".edl" for file in locations]
        with mock.patch("kintro.plex.open", mock.mock_open()) as patched_open:
            assert expected_files == kintro.plex.handle_episode(
                app_obj=app_obj,
                episode=episode,
                edit=kintro.decisions.DECISION_TYPES.cut,
                find_path=None,
                replace_path=None,
                dry_run=False,
                pbar=mocked_pbar,
                should_analyze=kintro.plex.Analyze.NoAnalyze,
            )
        assert patched_open.call_args_list == [mock.call(expected_file, "w") for expected_file in expected_files]
        patched_open.return_value.write.assert_has_calls(
            [
                mock.call(f"{marker.start / 1000} {marker.end / 1000} 0")
                for expected_file in expected_files
                for marker in markers
                if marker.type == "intro"
            ]
        )
        mocked_pbar.update.assert_called_once_with()
        assert any(
            f'start={marker.start / 1000} end={marker.end / 1000} file="{expected_file}"' in k[0][0]
            for k in app_obj["logger"].infos
            for expected_file in expected_files
            for marker in markers
            if marker.type == "intro"
        )


def describe_handle_episodes():
    pass
