"""Query PulseAudio status using pacmd commandline tool"""

import collections
import re
import subprocess


class PulseAudio:

	volume_re = re.compile('^set-sink-volume ([^ ]+) (.*)')
	mute_re = re.compile('^set-sink-mute ([^ ]+) ((?:yes)|(?:no))')
	default_sink_re = re.compile('^set-default-sink ([^ ]+)')

	def __init__(self):
		self._mute = collections.OrderedDict()
		self._volume = collections.OrderedDict()
		self._default_sink = None

	def update(self):
		proc = subprocess.Popen(['pacmd','dump'], stdout=subprocess.PIPE)

		for line in proc.stdout:
			line = line.decode("utf-8")
			volume_match = PulseAudio.volume_re.match(line)
			mute_match = PulseAudio.mute_re.match(line)
			default_sink_match = PulseAudio.default_sink_re.match(line)

			if volume_match:
				self._volume[volume_match.group(1)] = int(volume_match.group(2),16)
			elif mute_match:
				self._mute[mute_match.group(1)] = mute_match.group(2).lower() == "yes"
			elif default_sink_match:
				self._default_sink = default_sink_match.group(1).strip()


	def get_mute(self, sink=None):
		if not sink:
			sink = list(self._mute.keys())[0]

		return self._mute[sink]

	def get_volume(self, sink=None):
		if not sink:
			sink = list(self._volume.keys())[0]

		return self._volume[sink]

	def set_mute(self, mute, sink=None):
		if not sink:
			sink = list(self._mute.keys())[0]

		subprocess.Popen(['pacmd', 'set-sink-mute', sink, 'yes' if mute else 'no'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		self._mute[sink] = mute

	def set_volume(self, volume, sink=None):
		if not sink:
			sink = list(self._volume.keys())[0]

		subprocess.Popen(['pacmd', 'set-sink-volume', sink, hex(volume)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		self._volume[sink] = volume

	def get_default_sink(self):
		return self._default_sink

if __name__ == "__main__":
	pa = PulseAudio()
	pa.update()
	print(pa.get_mute(), pa.get_volume(), pa.get_default_sink())

