extends Control

onready var video_player = $MPFVideoPlayer

func _ready():
    # Connect to MPF events
    MPFConnector.connect("mpf_event", self, "_on_mpf_event")
    
    # Start video playing initially
    video_player.play()

func _on_mpf_event(event_name, data):
    print("Attract received event: ", event_name)
    
    match event_name:
        "mode_attract_started":
            video_player.play()
            
        "mode_attract_stopped", "game_started":
            # Handle transition to game scene
            # For now, just stop the video
            video_player.stop()
            
func _exit_tree():
    # Clean up the connection when scene exits
    if MPFConnector.is_connected("mpf_event", self, "_on_mpf_event"):
        MPFConnector.disconnect("mpf_event", self, "_on_mpf_event")
