"""Arpeggiator for midi input."""

import time
import random
import tulip




#tulip.seq_add_callback(midi_step, int(tulip.seq_ppq()/2))


class ArpeggiatorSynth:
    """Create arpeggios."""
    # State
    synth = None    # Downstream synthesizer object.
    current_active_notes = None    # Set of notes currently down on keyboard.
    arpeggiate_base_notes = None    # Set of notes currently driving the arpeggio.
    full_sequence = None    # List of notes in arpeggio (including direction and octave).
    current_note = None    # Last note sent to synth (i.e., next note-off).
    current_step = -1    # Current position in sequence.
    running = False    # Currently mid-sequence.    Goes false if no notes are playing.
    # UI control items
    active = False
    hold = False
    octaves = 1
    direction = "up"
    # Velocity for all the notes generated by the sequencer.
    velocity = 0.5
    # Notes at or above the split_note are always passed through live, not sequenced.
    split_note = 128    # Split is off the end of the keyboard, i.e., inactive.
    
    def __init__(self, synth, channel=0):
        self.synth = synth
        self.channel = channel    # This is just bookkeeping for my owner, not used.
        self.current_active_notes = set()
        self.arpeggiate_base_notes = set()
        self.full_sequence = []
        self.slot = -1
        self.step_callback = self.arp_step  # Ensure bound_method_obj created just once.

    def note_on(self, note, vel):
        if not self.active or note >= self.split_note:
            return self.synth.note_on(note, vel)
        if self.hold and not self.current_active_notes:
            # First note after all keys off resets hold set.
            self.arpeggiate_base_notes = set()
        # Adding keys to some already down.
        self.current_active_notes.add(note)
        # Because it's a set, can't get more than one instance of a base note.
        self.arpeggiate_base_notes.add(note)
        self._update_full_sequence()

    def note_off(self, note):
        if not self.active or note >= self.split_note:
            return self.synth.note_off(note)
        #print(self.current_active_notes, self.arpeggiate_base_notes)
        # Update our internal record of keys currently held down.
        self.current_active_notes.remove(note)
        if not self.hold:
            # If not hold, remove notes from active set when released.
            self.arpeggiate_base_notes.remove(note)
            self._update_full_sequence()

    def arp_step(self,t):
        if(self.running):
            # time is the actual event time for this event.
            self.next_note(time=t)

    def run(self):
        # Prepare to start a new sequence at the first note.
        self.current_step = -1
        # Semaphore to the run loop to start going.
        self.running = True
        self.slot = tulip.seq_add_callback(self.step_callback, int(tulip.seq_ppq()/2))

    def stop(self):
        self.running = False
        if(self.slot >= 0):
            tulip.seq_remove_callback(self.slot)
        
    def _update_full_sequence(self):
        """The full note loop given base_notes, octaves, and direction."""
        # Basic notes, ascending.
        basic_notes = sorted(self.arpeggiate_base_notes)
        # Apply octaves
        notes = []
        for o in range(self.octaves):
            notes = notes + [n + 12 * o for n in basic_notes]
        # Apply direction
        if self.direction == "down":
            notes = notes[::-1]
        elif self.direction == "updown":
            notes = notes + notes[-2:0:-1]
        self.full_sequence = notes
        if self.full_sequence and not self.running:
            self.run()


    def next_note(self, time=None):
        if self.current_note:
            self.synth.note_off(self.current_note)
            self.current_note = None
        if self.full_sequence:
            if self.direction == "rand":
                self.current_step = random.randint(0, len(self.full_sequence) - 1)
            else:
                self.current_step = (self.current_step + 1) % len(self.full_sequence)
            self.current_note = self.full_sequence[self.current_step]
            self.synth.note_on(self.current_note, self.velocity, time=time)
        else:
            self.stop()

    def control_change(self, control, value):
        return self.synth.control_change(control, value)

    def program_change(self, patch_number):
        return self.synth.program_change(patch_number)

    @property
    def amy_voices(self):
        return self.synth.amy_voices

    @property
    def num_voices(self):
        return self.synth.num_voices

    @property
    def patch_number(self):
        return self.synth.patch_number

    def cycle_octaves(self):
        self.octaves = 1 + (self.octaves % 3)

    def cycle_direction(self):
        if self.direction == 'up':
            self.direction = 'down'
        elif self.direction == 'down':
            self.direction = 'updown'
        elif self.direction == 'updown':
            self.direction = 'rand'
        else:
            self.direction = 'up'

    def set(self, arg, val=None):
        """Callback for external control."""
        #print("arp set", arg, val)
        #if self.active:
        #    return self.synth.set(arg, val)
        if arg == 'on':
            self.active = val
            # Reset hold state when on/off changes.
            self.arpeggiate_base_notes = set()
        elif arg == 'hold':
            self.hold = val
            # Copy across the current_active_notes after a change in hold.
            self.arpeggiate_base_notes = set(self.current_active_notes)
        elif arg == 'octaves':
            self.octaves = val
        elif arg == 'direction':
            self.direction = val
        self._update_full_sequence()

    # These should not be here.  Need to move arpeggiator.
    def _get_new_voices(self, num_voices):
        return self.synth._get_new_voices(num_voices)

    def release_voices(self):
        return self.synth.release_voices()

    def get_patch_state(self):
        return self.synth.get_patch_state()

    def set_patch_state(self, state):
        return self.synth.set_patch_state(state)
