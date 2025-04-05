extends VideoStreamPlayer


func _ready():
    # Connect to the 'finished' signal
    connect("finished", self, "_on_video_finished")

func _on_video_finished():
    # Loop the video
    play()
