/* mbed Microcontroller Library
 * Copyright (c) 2018-2018 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "AsyncOp.h"
#include "mbed_critical.h"

using namespace rtos;

AsyncOp::AsyncOp(Mutex *lock): _done(false), _signal(NULL), _signal_lock(lock)
{

}

void AsyncOp::wait()
{
    if (_done) {
        // Event has already occurred
        return;
    }

    // Construct semaphore to wait on
    Semaphore sem(0);

    // Atomically set the semaphore pointer and
    // check for completion
    _lock();
    bool local_done = _done;
    _signal = &sem;
    _unlock();

    if (!local_done) {
        sem.wait();
    }
}

void AsyncOp::complete()
{
    _lock();
    _done = true;
    if (_signal != NULL) {
        _signal->release();
    }
    _unlock();
}

void AsyncOp::_lock()
{
    if (_signal_lock) {
        _signal_lock->lock();
    } else {
        core_util_critical_section_enter();
    }
}

void AsyncOp::_unlock()
{
    if (_signal_lock) {
        _signal_lock->unlock();
    } else {
        core_util_critical_section_exit();
    }
}