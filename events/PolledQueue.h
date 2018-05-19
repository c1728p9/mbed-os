/* events
 * Copyright (c) 2018 ARM Limited
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

#ifndef POLLED_QUEUE_H
#define POLLED_QUEUE_H

#include "events/TaskQueue.h"
#include "platform/Callback.h"
#include "LinkedList.h"
namespace events {
/** \addtogroup events */



/** TaskQueue
 *
 *  Flexible task queue for dispatching tasks
 * @ingroup events
 */
class PolledQueue: public TaskQueue {
public:
    /** Create a PolledQueue
     *
     *  Create an event queue.
     */
    PolledQueue(mbed::Callback<void()> cb=NULL);

    virtual ~PolledQueue();

    virtual void post(TaskBase *event);

    virtual void cancel(TaskBase *event);

    void process();

protected:

    mbed::Callback<void()> _cb;
    LinkedList<TaskBase> _list;

};

}
#endif
