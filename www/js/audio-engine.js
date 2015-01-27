// Utility functions for the audio engine.
// 
// Call loadSoundList(list) with a json list of sounds and their names.
//
// Example:
// [
// 		{
// 			'name': 'jump',
// 			'url': 'http://localhost:8888/BashThatDev-Frontend/local_assets/jump.mp3'
//		},
//		{
//			'name': 'oops',
//			'url': 'http://localhost:8888/BashThatDev-Frontend/local_assets/oops.mp3'
//		}
//	];
//
//	This will load those sound into memory. To play a sound, simply use the
//	funtion play(name).


var context; //audio context 
var sounds = {};
var music = {};

//init the sound system 
function init() { 
	try { 
		// Make an audio context and try to make it "future safe".
		window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext;
		context = new AudioContext();
	} catch(e) { 
		alert('you need webaudio support'); 
	} 
}

window.addEventListener( 'load', init, false ); 

// Load a file via XMLHttpRequest, decode it
// and put the buffer and an identifier (id)
// for it in the sounds object.
function loadFile(url, id) { 
	var req = new XMLHttpRequest(); 
	req.open( "GET", url, true ); 
	req.responseType = "arraybuffer"; 
	req.onload = function() { 
		//decode the loaded data 
		context.decodeAudioData( req.response, function(buffer) { 
			sounds[id] = buffer;
		}); 
	}; 
	req.send(); 
} 

// Play sound [name] from the sounds object 
function play( name ) { 

	if (sounds[ name ] ) {
		// Create a source node from the buffer 
		var src = context.createBufferSource();  
		src.buffer = sounds[name]; 
		// Connect to the final output node (the speakers) 
		src.connect(context.destination); 
		// Play immediately 
		src.start(0);
	}

} 


// Load a list (json object) of sounds
function loadSoundList( sound_effects ) {
	

	sounds = {};
	// Loop through
	for (i = 0; i < sound_effects.length; i++) {
		var currentEntry = sound_effects[i];
		loadFile(currentEntry.url, currentEntry.name);
	}
}

function loadMusicFile( json ) {
	var req = new XMLHttpRequest(); 
	req.open( "GET", json.url, true ); 
	req.responseType = "arraybuffer"; 
	req.onload = function() { 
		//decode the loaded data 
		context.decodeAudioData( req.response, function(buffer) { 
			music['file'] = buffer;
			music['loop_start'] = json.loop_start;
			music['loop_point'] = json.loop_point;

			var src = context.createBufferSource();  
			src.buffer = music['file']; 
			// Connect to the final output node (the speakers) 
			src.connect(context.destination); 
			// Play immediately 
			src.noteOn(0);
		}); 
	}; 
	req.send();
}

