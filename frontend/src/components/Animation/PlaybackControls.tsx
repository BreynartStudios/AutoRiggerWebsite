import { useAnimationStore } from '../../stores/useAnimationStore';
import { formatTime } from '../../utils/formatters';

export default function PlaybackControls() {
  const {
    currentAnimation,
    isPlaying,
    playbackSpeed,
    loopEnabled,
    currentTime,
    duration,
    togglePlayback,
    setPlaybackSpeed,
    setLoopEnabled,
    setCurrentTime,
    setIsPlaying,
  } = useAnimationStore();

  if (!currentAnimation) return null;

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTime(parseFloat(e.target.value));
  };

  const jumpToStart = () => {
    setCurrentTime(0);
    setIsPlaying(false);
  };

  const jumpToEnd = () => {
    setCurrentTime(duration);
    setIsPlaying(false);
  };

  return (
    <div className="h-16 bg-gray-900 border-t border-gray-700 px-4 flex items-center gap-4 shrink-0">
      {/* Transport controls */}
      <div className="flex items-center gap-1">
        <ControlButton onClick={jumpToStart} title="Jump to start">
          |&lt;
        </ControlButton>
        <ControlButton onClick={togglePlayback} title={isPlaying ? 'Pause' : 'Play'}>
          {isPlaying ? '||' : '\u25B6'}
        </ControlButton>
        <ControlButton onClick={jumpToEnd} title="Jump to end">
          &gt;|
        </ControlButton>
      </div>

      {/* Timeline */}
      <div className="flex-1 flex items-center gap-3">
        <input
          type="range"
          min={0}
          max={duration || 1}
          step={0.01}
          value={currentTime}
          onChange={handleScrub}
          className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-sky-500"
        />
        <span className="text-xs text-gray-400 w-24 text-right font-mono">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>

      {/* Speed */}
      <div className="flex items-center gap-1">
        {[0.5, 1, 2].map((speed) => (
          <button
            key={speed}
            onClick={() => setPlaybackSpeed(speed)}
            className={`text-xs px-2 py-1 rounded transition-colors ${
              playbackSpeed === speed
                ? 'bg-sky-500 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {speed}x
          </button>
        ))}
      </div>

      {/* Loop toggle */}
      <button
        onClick={() => setLoopEnabled(!loopEnabled)}
        className={`text-xs px-2 py-1 rounded transition-colors ${
          loopEnabled
            ? 'bg-sky-500/20 text-sky-400'
            : 'text-gray-500 hover:text-gray-300'
        }`}
        title={loopEnabled ? 'Loop: ON' : 'Loop: OFF'}
      >
        Loop: {loopEnabled ? 'ON' : 'OFF'}
      </button>

      {/* Animation name */}
      <span className="text-xs text-gray-500 truncate max-w-32">
        {currentAnimation.name}
      </span>
    </div>
  );
}

function ControlButton({
  onClick,
  title,
  children,
}: {
  onClick: () => void;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition-colors text-sm"
    >
      {children}
    </button>
  );
}
