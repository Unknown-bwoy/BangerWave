# File Name: ui/search_view.py
import flet as ft
from typing import Dict, Any, Optional

class BangerWaveSearchView:
    """SearchView controller for the BangerWave application viewport."""
    
    def __init__(self, page: Any, state: Any, worker: Any, db: Any):
        # Store system dependency channels explicitly inside the instance scope
        self.page = page
        self.state = state
        self.worker = worker
        self.db = db
        
        # 1. Initialize an empty scrolling view list layout for tracking search components
        self.results_list = ft.ListView(expand=True, spacing=10, padding=10)
        
        # 2. Setup text box input field
        self.search_box = ft.TextField(
            hint_text="Search for songs, artists, or genres...",
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=8,
            on_submit=lambda e: self.page.run_task(self.execute_search, e)
        )

    async def execute_search(self, e):
        """Asynchronously triggers network link extraction using background worker threads."""
        query_text = self.search_box.value.strip()
        if not query_text:
            return

        # Empty out old visual tracks cards and post loading feedback spinners
        self.results_list.controls.clear()
        self.results_list.controls.append(
            ft.Row(controls=[ft.ProgressRing(), ft.Text(" Fetching matching track links...")])
        )
        self.page.update()

        # Safely hand the heavy scraping operation over to our isolated thread execution pool
        track_data = await self.worker.resolve_stream(query_text)
        self.results_list.controls.clear()

        if track_data:
            # Query the database to populate your popup folder selectors
            playlists = []
            if self.db:
                playlists = self.db.get_all_playlists()
            
            # Map saved folder rows to pop up actionable save triggers
            menu_items = [
                ft.PopupMenuItem(
                    text=f"Save to {pl['name']}",
                    on_click=lambda e, pl_id=pl["id"]: self.save_song_action(pl_id, track_data)
                ) for pl in playlists
            ]

            # Construct an immaculate Spotify-style visual tracking result card
            track_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=ft.Colors.BLUE_ACCENT_400),
                        ft.Column(
                            controls=[
                                ft.Text(track_data["title"], weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(
                                    value=f"Length: {int(track_data['duration'] // 60)}m {int(track_data['duration'] % 60)}s", 
                                    size=12, 
                                    color=ft.Colors.GREY_400
                                )
                            ], 
                            expand=True
                        ),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                    on_click=lambda _: self.inject_and_play(track_data)
                                ),
                                ft.PopupMenuButton(
                                    icon=ft.Icons.MORE_VERT_ROUNDED,
                                    items=menu_items
                                )
                            ]
                        )
                    ]
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER,
                padding=12,
                border_radius=8
            )
            self.results_list.controls.append(track_card)
        else:
            self.results_list.controls.append(ft.Text("No streaming entries resolved. Try another query."))
            
        self.page.update()

    def inject_and_play(self, track: Dict[str, Any]):
        """Injects unexpired HTTP stream links directly into the application state matrix."""
        print(f"[PLAYBACK TRIGGER] Initializing network audio stream for: {track['title']}")
        self.state.update_track(track)

    def save_song_action(self, playlist_id: int, track: Dict[str, Any]):
        """Triggers sequential database transactions to log track records inside SQLite tables."""
        if self.db:
            success = self.db.add_track_to_playlist(playlist_id, track)
            if success:
                print(f"[SAVE SUCCESS] Securely logged '{track['title']}' inside playlist ID: {playlist_id}")
                self.search_box.hint_text = f"Saved: {track['title'][:20]}..."
                self.page.update()

    def build(self) -> ft.Column:
        """Returns the completed search dashboard container column layout view."""
        return ft.Column(
            controls=[
                ft.Row(controls=[self.search_box, ft.ElevatedButton("Search", on_click=lambda e: self.page.run_task(self.execute_search, e))]),
                ft.Container(content=self.results_list, expand=True)
            ],
            expand=True
        )
