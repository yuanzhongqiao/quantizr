import { ValueIntf } from "../../Interfaces";
import { Value } from "../../Value";
import { Comp } from "../base/Comp";
import { CheckboxInput } from "./CheckboxInput";
import { Label } from "./Label";

export class Checkbox extends Comp {
    outterClassName: string;

    /* To turn this into a slider switch, just add 'form-switch' to layoutClass style */
    constructor(public label: string = null, attribs: any = null, private valueIntf: ValueIntf, private layoutClass: string = null) {
        super(attribs);

        this.valueIntf = this.valueIntf || new Value<string>(this, "val");
        this.outterClassName = this.attribs.className || "";
        this.layoutClass = this.layoutClass || "inline-flex items-center";
        this.tag = "span";
    }

    override preRender(): boolean | null {
        let cbInput = null;
        // there is also a 'custom-control-inline' that could be used instead of 'inline-checkbox'
        // but it adds space to the right NOTE: custom-switch or custom-checkbox will work here with
        // all other things being identical! The custom-switch shows a little slider switch button
        // instead of a box with a check.
        this.attribs.className = "relative flex items-start mt-1 " + this.layoutClass + " " + this.outterClassName + " cursor-pointer";
        this.children = [
            cbInput = new CheckboxInput({
                type: "checkbox",
                className: "w-6 h-6 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            }, null, this.valueIntf),
            new Label(this.label || "", {
                className: "ml-2 cursor-pointer " + (this.label ? "checkboxLabel" : ""),
                htmlFor: cbInput.getId(),
                title: this.attribs.title
            })
        ];
        return true;
    }
}
