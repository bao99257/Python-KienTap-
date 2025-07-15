import React, { useState, useEffect } from 'react';
import './CountdownTimer.css';

const CountdownTimer = ({ 
  endTime, 
  onTimeUp, 
  size = 'medium',
  showLabels = true,
  className = ''
}) => {
  const [timeLeft, setTimeLeft] = useState({
    hours: 0,
    minutes: 0,
    seconds: 0,
    total: 0
  });

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const endTimeMs = new Date(endTime).getTime();
      const difference = endTimeMs - now;

      if (difference > 0) {
        const hours = Math.floor(difference / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        setTimeLeft({
          hours,
          minutes,
          seconds,
          total: difference
        });
      } else {
        setTimeLeft({
          hours: 0,
          minutes: 0,
          seconds: 0,
          total: 0
        });
        
        if (onTimeUp) {
          onTimeUp();
        }
      }
    };

    // Calculate immediately
    calculateTimeLeft();

    // Update every second
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [endTime, onTimeUp]);

  const formatTime = (time) => {
    return time.toString().padStart(2, '0');
  };

  const getTimeDisplay = () => {
    if (timeLeft.total <= 0) {
      return "Đã kết thúc";
    }

    return `${formatTime(timeLeft.hours)}:${formatTime(timeLeft.minutes)}:${formatTime(timeLeft.seconds)}`;
  };

  const isUrgent = timeLeft.total <= 300000; // 5 minutes
  const isVeryUrgent = timeLeft.total <= 60000; // 1 minute

  return (
    <div className={`countdown-timer ${size} ${className} ${isUrgent ? 'urgent' : ''} ${isVeryUrgent ? 'very-urgent' : ''}`}>
      {showLabels && (
        <div className="countdown-label">
          {timeLeft.total > 0 ? "Kết thúc trong:" : "Đã kết thúc"}
        </div>
      )}
      
      <div className="countdown-display">
        {timeLeft.total > 0 ? (
          <div className="time-blocks">
            <div className="time-block">
              <span className="time-number">{formatTime(timeLeft.hours)}</span>
              {showLabels && <span className="time-unit">Giờ</span>}
            </div>
            <div className="time-separator">:</div>
            <div className="time-block">
              <span className="time-number">{formatTime(timeLeft.minutes)}</span>
              {showLabels && <span className="time-unit">Phút</span>}
            </div>
            <div className="time-separator">:</div>
            <div className="time-block">
              <span className="time-number">{formatTime(timeLeft.seconds)}</span>
              {showLabels && <span className="time-unit">Giây</span>}
            </div>
          </div>
        ) : (
          <div className="time-up">
            <i className="fas fa-clock"></i>
            <span>Đã kết thúc</span>
          </div>
        )}
      </div>

      {/* Progress bar for visual effect */}
      {timeLeft.total > 0 && (
        <div className="countdown-progress">
          <div 
            className="progress-bar"
            style={{
              width: `${Math.max(0, Math.min(100, (timeLeft.total / (24 * 60 * 60 * 1000)) * 100))}%`
            }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default CountdownTimer;
