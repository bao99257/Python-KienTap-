import React, { useState, useEffect } from 'react';
import './FlashSaleTimeline.css';

const FlashSaleTimeline = ({ 
  programs = [], 
  onTimeSlotSelect, 
  currentProgram = null,
  className = '' 
}) => {
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    // Update current time every minute
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Auto-select current program if available
    if (currentProgram && !selectedSlot) {
      setSelectedSlot(currentProgram.id);
      if (onTimeSlotSelect) {
        onTimeSlotSelect(currentProgram);
      }
    }
  }, [currentProgram, selectedSlot, onTimeSlotSelect]);

  const getTimeSlotStatus = (program) => {
    const now = new Date();
    const startTime = new Date(program.start_time);
    const endTime = new Date(program.end_time);

    if (now < startTime) {
      return 'upcoming';
    } else if (now >= startTime && now <= endTime) {
      return 'active';
    } else {
      return 'ended';
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const getTimeUntilStart = (startTime) => {
    const now = new Date();
    const start = new Date(startTime);
    const diff = start - now;
    
    if (diff <= 0) return null;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const handleSlotClick = (program) => {
    const status = getTimeSlotStatus(program);
    
    // Only allow selection of active or upcoming programs
    if (status === 'ended') return;
    
    setSelectedSlot(program.id);
    if (onTimeSlotSelect) {
      onTimeSlotSelect(program);
    }
  };

  const getSlotIcon = (status) => {
    switch (status) {
      case 'active':
        return 'fas fa-fire';
      case 'upcoming':
        return 'fas fa-clock';
      case 'ended':
        return 'fas fa-check-circle';
      default:
        return 'fas fa-clock';
    }
  };

  const getStatusLabel = (status, program) => {
    switch (status) {
      case 'active':
        return 'Đang diễn ra';
      case 'upcoming':
        const timeUntil = getTimeUntilStart(program.start_time);
        return timeUntil ? `Còn ${timeUntil}` : 'Sắp bắt đầu';
      case 'ended':
        return 'Đã kết thúc';
      default:
        return '';
    }
  };

  return (
    <div className={`flash-sale-timeline ${className}`}>
      <div className="timeline-header">
        <h3 className="timeline-title">
          <i className="fas fa-bolt"></i>
          Flash Sale Hôm Nay
        </h3>
        <div className="current-time">
          {currentTime.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
          })}
        </div>
      </div>

      <div className="timeline-slots">
        {programs.length === 0 ? (
          <div className="no-programs">
            <i className="fas fa-calendar-times"></i>
            <span>Không có chương trình Flash Sale nào hôm nay</span>
          </div>
        ) : (
          programs.map((program) => {
            const status = getTimeSlotStatus(program);
            const isSelected = selectedSlot === program.id;
            const isClickable = status !== 'ended';

            return (
              <div
                key={program.id}
                className={`timeline-slot ${status} ${isSelected ? 'selected' : ''} ${isClickable ? 'clickable' : ''}`}
                onClick={() => handleSlotClick(program)}
              >
                <div className="slot-time">
                  {formatTime(program.start_time)}
                </div>
                
                <div className="slot-content">
                  <div className="slot-header">
                    <i className={getSlotIcon(status)}></i>
                    <span className="slot-name">{program.name}</span>
                  </div>
                  
                  <div className="slot-status">
                    {getStatusLabel(status, program)}
                  </div>
                  
                  {program.items_count && (
                    <div className="slot-items-count">
                      {program.items_count} sản phẩm
                    </div>
                  )}
                </div>

                {status === 'active' && (
                  <div className="active-indicator">
                    <div className="pulse-dot"></div>
                  </div>
                )}

                {isSelected && (
                  <div className="selected-indicator">
                    <i className="fas fa-check"></i>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Legend */}
      <div className="timeline-legend">
        <div className="legend-item">
          <i className="fas fa-fire legend-icon active"></i>
          <span>Đang diễn ra</span>
        </div>
        <div className="legend-item">
          <i className="fas fa-clock legend-icon upcoming"></i>
          <span>Sắp diễn ra</span>
        </div>
        <div className="legend-item">
          <i className="fas fa-check-circle legend-icon ended"></i>
          <span>Đã kết thúc</span>
        </div>
      </div>
    </div>
  );
};

export default FlashSaleTimeline;
