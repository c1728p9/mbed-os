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

#ifndef USBPHYCMSIS_H
#define USBPHYCMSIS_H

#include "mbed.h"
#include "USBPhy.h"
#include "Driver_USBD.h"


class USBPhyCMSIS : public USBPhy {
public:
    USBPhyCMSIS(const ARM_DRIVER_USBD *phy,
                const usb_ep_table_t *endpoint_table,
                void (*isr_handler)() = NULL,
                IRQn_Type irq_num = (IRQn_Type)0);
    virtual ~USBPhyCMSIS();
    virtual void init(USBPhyEvents *events);
    virtual void deinit();
    virtual bool powered();
    virtual void connect();
    virtual void disconnect();
    virtual void configure();
    virtual void unconfigure();
    virtual void sof_enable();
    virtual void sof_disable();
    virtual void set_address(uint8_t address);
    virtual void remote_wakeup();
    virtual const usb_ep_table_t* endpoint_table();

    virtual uint32_t ep0_set_max_packet(uint32_t max_packet);
    virtual void ep0_setup_read_result(uint8_t *buffer, uint32_t size);
    virtual void ep0_read(uint8_t *buffer, uint32_t size);
    virtual uint32_t ep0_read_result();
    virtual void ep0_write(uint8_t *buffer, uint32_t size);
    virtual void ep0_stall();

    virtual bool endpoint_add(usb_ep_t endpoint, uint32_t max_packet, usb_ep_type_t type);
    virtual void endpoint_remove(usb_ep_t endpoint);
    virtual void endpoint_stall(usb_ep_t endpoint);
    virtual void endpoint_unstall(usb_ep_t endpoint);

    virtual bool endpoint_read(usb_ep_t endpoint, uint8_t *data, uint32_t size);
    virtual uint32_t endpoint_read_result(usb_ep_t endpoint);
    virtual bool endpoint_write(usb_ep_t endpoint, uint8_t *data, uint32_t size);
    virtual void endpoint_abort(usb_ep_t endpoint);

    virtual void process();

protected:

    static void _usbisr();

private:
    const ARM_DRIVER_USBD *_phy;
    const usb_ep_table_t *_table;
    USBPhyEvents *_events;
    bool _sof_on;
    void (*_irq_handler)();
    IRQn_Type _irq;
    uint16_t _ep0_max_packet;
    bool _set_addr;
    uint8_t _addr;

    static USBPhyCMSIS *_instance;
    static void _event_handler_device(uint32_t event);
    static void _event_handler_endpoint(uint8_t ep_addr, uint32_t event);


};

#endif