import QtQuick 2.1

Row {
    id: speech
    property alias type: country.text
	property alias text: display.text
	property alias display: display
	property alias speaker: speaker
	visible: display.text
	spacing: 6
	signal clicked
    
    function getWidth() {
        return display.paintedWidth + country.paintedWidth + speaker.width + spacing * 2
    }
    
    function getHeight() {
        return Math.max(display.paintedHeight, speaker.height)
    }
		
    Text {
        id: country
        anchors.verticalCenter: parent.verticalCenter 
		font { pixelSize: 15 }
		color: "#a0a0a0"
    }
    
	Text { 
		id: display
        anchors.verticalCenter: parent.verticalCenter 
		font { pixelSize: 15 }
		color: "#5da6ce"
	}
	
	Image {
		id: speaker
		source: "image/speaker.png"
		anchors.verticalCenter: parent.verticalCenter 
        opacity: 0.5
        
		states: State {
			name: "hovered"
			PropertyChanges { target: speaker; opacity: 1.0 }
		}
		
		transitions: Transition {
			NumberAnimation { properties: "opacity"; duration: 350 }
		}
		
		MouseArea {
			id: mouseArea
			anchors.fill: speaker
            hoverEnabled: true
			
			onClicked: speech.clicked()
            
			onEntered: {
                speaker.state = "hovered"
                mouseArea.cursorShape = Qt.PointingHandCursor
            }
            
			onExited: {
                speaker.state = ""
                mouseArea.cursorShape = Qt.ArrowCursor
            }
            
			onReleased: { 
                speaker.state = mouseArea.containsMouse ? "hovered" : ""
            }
		}
	}
}
