/** @odoo-module **/

import { registry } from "@web/core/registry";

const toggleFullscreen = {
    type: "ir.actions.client",
    tag: "toggle_form_fullscreen",
    target: "current",
}

registry.category("actions").add("toggle_form_fullscreen", async function (env, action) {
    const formView = env.targetElement.closest('.o_form_view');
    if (!formView) return false;

    formView.classList.toggle('o_form_full_width');

    const button = formView.querySelector('button[name="action_toggle_fullscreen"] i');
    if (button) {
        if (formView.classList.contains('o_form_full_width')) {
            button.classList.replace('fa-expand', 'fa-compress');
        } else {
            button.classList.replace('fa-compress', 'fa-expand');
        }
    }

    return false;
});