# File Name: ui/search_view.py
from typing import Any, Dict

if __package__:
    from .flet_compat import ft
else:
    from flet_compat import ft


class BangerWaveSearchView:
    """SearchView controller for the BangerWave application viewport."""
    def __init__(self, page: Any, state: Any, worker: Any):
        # Inject core system layer pointers safely
        self.page = page
        self.state = state
        self.worker = worker
        
        # 1. Initialize an empty scrolling view list for track results
        self.results_list = ft.ListView(expand=True, spacing=10, padding=10)
        
        # 2. Setup your text input search layout control field
        self.search_box = ft.TextField(
            hint_text="Search for songs, artists, or genres...",
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=8,
            on_submit=lambda e: self.page.run_task(self.execute_search,e)
        )

    async def execute_search(self, e):
        """Asynchronously triggers network link extraction using background worker threads."""
        query_text = self.search_box.value.strip()
        if not query_text:
            return

        # Clear out previous search iterations and present an active loading spinner ring
        self.results_list.controls.clear()
        self.results_list.controls.append(
            ft.Row([ft.ProgressRing(), ft.Text(" Fetching matching track links...")])
        )
        self.page.update()

        # Delegate the blocking network I/O scrape safely onto the worker executor pool
        track_data = await self.worker.resolve_stream(query_text)
        self.results_list.controls.clear()

        if track_data:
            # 3. Construct an immaculate Spotify-style track record display card component
            track_card = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=ft.Colors.GREEN_ACCENT_400),
                    ft.Column([
                        ft.Text(track_data["title"], weight=ft.FontWeight.BOLD),
                        ft.Text(
                            value=f"Length: {int(track_data['duration'] // 60)}m {int(track_data['duration'] % 60)}s", 
                            size=12, 
                            color=ft.Colors.GREY_400
                        )
                    ], expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW_ROUNDED,
                        on_click=lambda _: self.inject_and_play(track_data)
                    )
                ]),
                bgcolor=ft.Colors.SURFACE_CONTAINER,
                padding=12,
                border_radius=8
            )
            self.results_list.controls.append(track_card)
        else:
            self.results_list.controls.append(ft.Text("No streaming entries resolved. Try another query."))
            
        self.page.update()

    def inject_and_play(self, track: Dict[str, Any]):
        """Injects unexpired HTTP stream links directly into the core app state layer."""
        print(f"[PLAYBACK TRIGGER] Initializing network audio stream for: {track['title']}")
        # Mutates the observer variable state layer to alert visual elements
        self.state.update_track(track)

    def build(self) -> Any:
        """Returns the completed search dashboard container column layout view."""
        return ft.Column(
            controls=[
                ft.Row([
                    self.search_box, 
                    ft.ElevatedButton("Search", on_click=lambda e: self.page.run_task(self.execute_search,e))
                ]),
                ft.Container(content=self.results_list, expand=True)
            ],
            expand=True
        )
