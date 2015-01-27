/**
 * evarglice
 * minimalistic event delegation.
 * 
 * @version 0.1.1
 * @author Mikael Jorhult
 * @license http://mikaeljorhult.mit-license.org MIT
 *
 * Project repository: https://github.com/mikaeljorhult/evarglice
 */
evarglice = {
	doc: null,
	event_listen: null,
	
	bind: function(type, object, func) {
		for(var i = 0, length = object.length; i < length; i++) {
			if(this.event_listen) {
				object[i].addEventListener(type, func, false);
			} else {
				object[i].attachEvent('on' + type, func);
			}
		}
		
		return object;
	},
	
	trigger: function(type, object) {
		for(var i = 0, length = object.length; i < length; i++) {
			if((object[i][type] || false) && typeof object[i][type] == 'function') {
				object[i][type](object[i]);
			}
		}
		
		return object;
	},
	
	unbind: function(type, object, func) {
		for(var i = 0, length = object.length; i < length; i++) {
			if(this.event_listen) {
				object[i].removeEventListener(type, func, false);
			} else {
				object[i].detachEvent('on' + type, func);
			}
		}
		
		return object;
	},
	
	init: function() {
		this.doc = document;
		this.event_listen = (this.doc.addEventListener ? true : false);
		return this;
	}
}.init();
