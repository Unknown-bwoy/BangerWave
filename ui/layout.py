from typing import Any

if __package__:
    from .flet_compat import ft
    from .search_view import BangerWaveSearchView
else:
    from flet_compat import ft
    from search_view import BangerWaveSearchView


class BangerWaveLayout:
    """Master Viewport Panel Framework for BangerWave using clean top-level imports."""

    def __init__(self, page: Any, state: Any, worker: Any):
        self.page = page
        self.state = state
        self.worker = worker
        
        self.page.title = "BangerWave"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK
          
        # Core active tracking properties bound to class memory
        self.track_title_label = ft.Text(value="No Track Selected", weight=ft.FontWeight.BOLD, size=14)
        self.track_artist_label = ft.Text(value="Unknown Artist", size=11, color=ft.Colors.GREY_400)
        self.play_button = ft.IconButton(icon=ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED, icon_size=36, icon_color=ft.Colors.BLUE_ACCENT_400)
        self.volume_slider = ft.Slider(width=100,min=0,max=100,value=80,on_change=self.on_state_changed)
    def _build_sidebar(self) -> Any:
        """Returns a fixed left panel container for main navigation."""
        return ft.Container(
            content=ft.Column([
                ft.Text("BangerWave", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT_400),
                ft.Divider(),
                ft.Row([ft.Icon(ft.Icons.SEARCH_ROUNDED), ft.Text("Search Dashboard")]),
                ft.Row([ft.Icon(ft.Icons.LIBRARY_MUSIC_ROUNDED), ft.Text("Your Playlists")])
            ], spacing=15),
            width=230,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            padding=15,
            border_radius=8,
        )

    def _build_viewport(self) -> Any:
        """Returns an expanding fluid panel container embedding the active search display."""
        search_panel = BangerWaveSearchView(self.page, self.state, self.worker)
        return ft.Container(
            content=search_panel.build(), 
            expand=True,
            bgcolor=ft.Colors.BLACK,
            padding=15,
        )

    def _build_player_bar(self) -> Any:
        """Returns a fixed bottom console container block for track timeline controls."""
        left_zone = ft.Container(
            content=ft.Column([
                # ──► LINKED: Mount your tracking variable boxes directly into the frame tree
                self.track_title_label,
                self.track_artist_label,
            ]),
            width=200,
        )
         
        center_zone = ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.Icons.SHUFFLE_ROUNDED, icon_size=18),
                # ──► LINKED: Mount your class control tracking play button here
                self.play_button,
                ft.IconButton(icon=ft.Icons.REPEAT_ROUNDED, icon_size=18),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text(value="0:00", size=11),
                ft.Slider(expand=True, min=0, max=100, value=0, active_color=ft.Colors.BLUE_ACCENT_400),
                ft.Text(value="0:00", size=11),
            ])
        ], expand=True)

                # Update right_zone inside _build_player_bar to use your tracking slider property:
        right_zone = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, size=18),
                self.volume_slider # ──► LINKED: Mounts your class control instance directly here
            ]),
            width=200,
        )

        return ft.Container(
            content=ft.Row([
                left_zone,
                center_zone,
                right_zone,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            height=90,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            padding=15,
            border_radius=12,
        )

    def assemble(self) -> None:
        """Assembles and renders the structural panel arrays directly into the page."""
        self.page.clean()

        main_workspace = ft.Row([
            self._build_sidebar(),
            self._build_viewport(),
        ], expand=True)

        self.page.add(
            ft.Column([
                main_workspace,
                self._build_player_bar(),
            ], expand=True)
        ) 


        # ──► RUNNING: Binds your subscription loop securely right as visual frames load
        self.state.subscribe(self.on_state_changed)
    def on_vol_changed(self,e) -> None: 
        """Fires whenever the user drags the vol slider interface bar.""" 
        normalized_vol = self.volume_slider.value / 100 
        #Mutate the system state engine threshold directly 
        self.state.set_volume(normalized_vol) 
        print(f"[VOLUME SYNC] Normalising core audio thresholds down to: {normalized_vol:.2f}") 



    def on_state_changed(self) -> None:
        """Fires automatically whenever our single source of truth state changes."""
        track = self.state.current_track
        if track:
            self.track_title_label.value = track.get("title", "Unknown Track")
            self.track_artist_label.value = "Web Stream Asset"
            
            if self.state.is_playing:
                self.play_button.icon = ft.Icons.PAUSE_CIRCLE_FILLED_ROUNDED
            else:
                self.play_button.icon = ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED
       
        self.page.update() 


#TO Do i will try to figure where each syntax is supposed to be and continue from there