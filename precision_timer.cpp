#include <iostream>
#include <chrono>
#include <thread>
#include <windows.h>

class PrecisionTimer {
private:
    LARGE_INTEGER frequency;
    
public:
    PrecisionTimer() {
        // 고해상도 타이머 초기화
        QueryPerformanceFrequency(&frequency);
        
        // Windows 멀티미디어 타이머 정밀도 설정 (1ms)
        timeBeginPeriod(1);
    }
    
    ~PrecisionTimer() {
        timeEndPeriod(1);
    }
    
    // 마이크로초 단위로 현재 시간 반환
    long long getCurrentTimeMicros() {
        LARGE_INTEGER counter;
        QueryPerformanceCounter(&counter);
        return (counter.QuadPart * 1000000) / frequency.QuadPart;
    }
    
    // 정밀한 대기 (마이크로초 단위)
    void preciseWaitMicros(long long microseconds) {
        long long startTime = getCurrentTimeMicros();
        long long endTime = startTime + microseconds;
        
        // 큰 지연은 Sleep 사용
        if (microseconds > 10000) {  // 10ms 이상
            Sleep((DWORD)((microseconds - 1000) / 1000));  // 1ms 여유두고 Sleep
        }
        
        // 마지막 구간은 busy wait
        while (getCurrentTimeMicros() < endTime) {
            // CPU yield for better performance
            YieldProcessor();
        }
    }
    
    // 특정 시간까지 정밀 대기
    void waitUntilMicros(long long targetTimeMicros) {
        long long currentTime = getCurrentTimeMicros();
        if (targetTimeMicros > currentTime) {
            preciseWaitMicros(targetTimeMicros - currentTime);
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: precision_timer <microseconds_to_wait>" << std::endl;
        return 1;
    }
    
    long long waitTime = std::stoll(argv[1]);
    PrecisionTimer timer;
    
    std::cout << "Starting precise wait for " << waitTime << " microseconds..." << std::endl;
    
    long long startTime = timer.getCurrentTimeMicros();
    timer.preciseWaitMicros(waitTime);
    long long endTime = timer.getCurrentTimeMicros();
    
    long long actualWaitTime = endTime - startTime;
    long long error = actualWaitTime - waitTime;
    
    std::cout << "Requested: " << waitTime << " μs" << std::endl;
    std::cout << "Actual: " << actualWaitTime << " μs" << std::endl;
    std::cout << "Error: " << error << " μs" << std::endl;
    
    return 0;
}
