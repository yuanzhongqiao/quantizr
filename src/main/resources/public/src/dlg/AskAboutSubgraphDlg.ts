import { Constants as C } from "../Constants";
import { DialogBase } from "../DialogBase";
import * as J from "../JavaIntf";
import { S } from "../Singletons";
import { ValHolder, ValidatorRuleName } from "../ValHolder";
import { Comp, ScrollPos } from "../comp/base/Comp";
import { Button } from "../comp/core/Button";
import { ButtonBar } from "../comp/core/ButtonBar";
import { Div } from "../comp/core/Div";
import { TextArea } from "../comp/core/TextArea";
import { AIAnswerDlg } from "./AIAnswerDlg";

export class AskAboutSubgraphDlg extends DialogBase {
    questionState: ValHolder = new ValHolder("", [
        { name: ValidatorRuleName.REQUIRED },
        { name: ValidatorRuleName.MINLEN, payload: 10 }
    ]);
    textScrollPos = new ScrollPos();
    textArea: TextArea;

    constructor(public nodeId: string) {
        super("Question about Content", "appModalContMediumWidth");
        this.onMount(() => { this.textArea?.focus(); });
    }

    renderDlg(): Comp[] {
        return [
            new Div(null, null, [
                this.textArea = new TextArea("Ask a Question...", { rows: 15 }, this.questionState, null, false, 3, this.textScrollPos),
                new ButtonBar([
                    new Button("Submit", this.askQuestion, null, "-primary"),
                    new Button("Close", this._close)
                ], "mt-3")
            ])
        ];
    }

    askQuestion = async () => {
        if (!this.validate()) {
            return;
        }

        // asks a question about the subgraph of this tree
        const res = await S.rpcUtil.rpc<J.AskSubGraphRequest, J.AskSubGraphResponse>("askSubGraph", {
            nodeId: this.nodeId,
            question: this.questionState.getValue(),
            nodeIds: S.nodeUtil.getSelNodeIdsArray()
        });

        this.close();

        if (res.code == C.RESPONSE_CODE_OK) {
            new AIAnswerDlg(res.answer).open();
        }
    }
}
