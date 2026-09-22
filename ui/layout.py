# File Name: ui/layout.py
import flet as ft
from typing import Any
from ui.search_view import BangerWaveSearchView

class BangerWaveLayout:
    """Master Viewport Panel Framework for BangerWave using clean top-level imports."""

    def __init__(self, page: Any, state: Any, worker: Any, db: Any):
        # 1. Structural Dependency Injection Storage
        self.page = page
        self.state = state
        self.worker = worker
        self.db = db
        
        # 2. Configure Global Window Parameters to match dark theme guidelines
        self.page.title = "BangerWave Stream Client"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK
          
        # 3. Persistent Core Active Tracking Control Elements bound to class memory
        self.track_title_label = ft.Text(value="No Track Selected", weight=ft.FontWeight.BOLD, size=14)
        self.track_artist_label = ft.Text(value="Unknown Artist", size=11, color=ft.Colors.GREY_400)
        self.play_button = ft.IconButton(icon=ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED, icon_size=36, icon_color=ft.Colors.BLUE_ACCENT_400)
        self.volume_slider = ft.Slider(width=100, min=0, max=100, value=80, on_change=self.on_volume_changed)
        self.playlists_column = ft.Column(spacing=10)
    
    def _build_sidebar(self) -> ft.Container:
        """Returns a fixed left panel container for main navigation and folders."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("BangerWave", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT_400),
                    ft.Divider(),
                    ft.Row(controls=[ft.Icon(ft.Icons.SEARCH_ROUNDED), ft.Text("Search Dashboard")]),
                    
                    # Header sub-row layout incorporating an interactive folder generation action click
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LIBRARY_MUSIC_ROUNDED),
                            ft.Text("Your Playlists", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.ADD_BOX_ROUNDED, 
                                icon_color=ft.Colors.BLUE_ACCENT_400,
                                icon_size=20,
                                on_click=lambda e: self.show_create_playlist_modal()
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    # Dynamic sidebar sub-column holding database loaded directories
                    ft.Container(content=self.playlists_column, expand=True)
                ], 
                spacing=15
            ),
            width=230,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            padding=15,
            border_radius=8,
        )

    def _build_viewport(self) -> ft.Container:
        """Returns an expanding fluid panel container embedding the active search display view."""
        search_panel = BangerWaveSearchView(self.page, self.state, self.worker, self.db)
        return ft.Container(
            content=search_panel.build(), 
            expand=True,
            bgcolor=ft.Colors.BLACK,
            padding=15,
        )

    def _build_player_bar(self) -> ft.Container:
        """Returns a fixed bottom console container block for track timeline controls."""
        left_zone = ft.Container(
            content=ft.Column(
                controls=[
                    self.track_title_label,
                    self.track_artist_label,
                ]
            ),
            width=200,
        )
         
        center_zone = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(icon=ft.Icons.SHUFFLE_ROUNDED, icon_size=18),
                        self.play_button,
                        ft.IconButton(icon=ft.Icons.REPEAT_ROUNDED, icon_size=18),
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        ft.Text(value="0:00", size=11),
                        ft.Slider(expand=True, min=0, max=100, value=0, active_color=ft.Colors.BLUE_ACCENT_400),
                        ft.Text(value="0:00", size=11),
                    ]
                )
            ], 
            expand=True
        )

        right_zone = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, size=18),
                    self.volume_slider,
                ]
            ),
            width=200,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    left_zone,
                    center_zone,
                    right_zone,
                ], 
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            height=90,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            padding=15,
            border_radius=12,
        )

    def show_create_playlist_modal(self) -> None:
        """Assembles and overlays a modal input alert dialog block onto the active interface view."""
        playlist_input = ft.TextField(hint_text="e.g., Synthwave Hits, Chill Vibe Mix", autofocus=True)

        def close_dialog(_):
            dialog.open = False
            self.page.update()

        def confirm_creation(_):
            name = playlist_input.value.strip()
            if name and self.db:
                success = self.db.create_playlist(name)
                if success:
                    print(f"[PLAYLIST CREATED] Securely logged folder: {name}")
                    self.load_playlists_into_sidebar()
            close_dialog(None)

        dialog = ft.AlertDialog(
            title=ft.Text("Create New Playlist"),
            content=playlist_input,
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Create", bgcolor=ft.Colors.BLUE_ACCENT_400, on_click=confirm_creation)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def load_playlists_into_sidebar(self) -> None:
        """Queries SQLite data engines and builds readable folder rows inside the navigation grid."""
        if not self.db:
            return
            
        playlist_rows = self.db.get_all_playlists()
        self.playlists_column.controls.clear()
        
        for pl in playlist_rows:
            self.playlists_column.controls.append(
                ft.GestureDetector(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, size=16, color=ft.Colors.GREY_400),
                            ft.Text(pl["name"], size=13, overflow=ft.TextOverflow.ELLIPSIS)
                        ], 
                        spacing=10
                    ),
                    on_tap=lambda e, pl_id=pl["id"]: print(f"Playlist Clicked ID: {pl_id}")
                )
            )
        self.page.update()

    def on_volume_changed(self, e) -> None:
        """Fires whenever the user drags the volume slider interface control bar."""
        normalized_volume = self.volume_slider.value / 100
        self.state.set_volume(normalized_volume)
        print(f"[VOLUME SYNC] Normalizing core audio thresholds down to: {normalized_volume:.2f}")

    def on_state_changed(self) -> None:
        """Fires automatically whenever our single source of truth state layer updates."""
        track = self.state.current_track
        if track:
            self.track_title_label.value = track.get("title", "Unknown Track")
            self.track_artist_label.value = "Web Stream Asset"
            
            if self.state.is_playing:
                self.play_button.icon = ft.Icons.PAUSE_CIRCLE_FILLED_ROUNDED
            else:
                self.play_button.icon = ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED
                
        self.page.update()

    def assemble(self) -> None:
        """Assembles and renders the structural panel arrays directly into the page."""
        self.page.clean()

        main_workspace = ft.Row(
            controls=[
                self._build_sidebar(),
                self._build_viewport(),
            ], 
            expand=True
        )

        self.page.add(
            ft.Column(
                controls=[
                    main_workspace,
                    self._build_player_bar(),
                ], 
                expand=True
            )
        ) 
        # Register the state subscription loop and initialize playlist rows at boot
        self.state.subscribe(self.on_state_changed)
        self.load_playlists_into_sidebar()
