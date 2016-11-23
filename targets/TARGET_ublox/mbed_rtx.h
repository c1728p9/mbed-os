/* mbed Microcontroller Library
 * Copyright (c) 2016 u-blox
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

#ifndef MBED_MBED_RTX_H
#define MBED_MBED_RTX_H

#if defined(TARGET_HI2110)

#ifndef INITIAL_SP
#define INITIAL_SP              (0x01000000 + 0x05000 - 256)
#endif

#ifndef OS_THREAD_NUM
#define OS_THREAD_NUM              6
#endif
#ifndef OS_MAINSTKSIZE
#define OS_MAINSTKSIZE          128
#endif
#ifndef OS_CLOCK
#define OS_CLOCK                48000000
#endif
#endif

#endif  // MBED_MBED_RTX_H
