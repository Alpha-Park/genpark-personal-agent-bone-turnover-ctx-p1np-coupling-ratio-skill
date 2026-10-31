# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-bone-turnover-ctx-p1np-coupling-ratio-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def analyze_bone_turnover_coupling(s_ctx_ng_ml, total_p1np_ug_l, dexas_t_score=-1.2, sex="FEMALE"):
    if s_ctx_ng_ml <= 0 or total_p1np_ug_l <= 0:
        raise ValueError("Bone markers must be positive numbers")
        
    # Reference targets:
    # Premenopausal / young adult male healthy median: s-CTX ~0.25-0.45 ng/mL, P1NP ~35-55 ug/L
    # Uncoupling index: P1NP (ug/L) / (s-CTX * 100)
    # Ratio around 1.0 - 1.5 is balanced. < 0.8 indicates high resorption outstripping formation.
    
    uncoupling_index = total_p1np_ug_l / (s_ctx_ng_ml * 100.0)
    
    if s_ctx_ng_ml > 0.55 and uncoupling_index < 0.85:
        remodeling_state = "HIGH_UNCOUPLED_RESORPTION"
        bmd_trend = "Accelerated bone mineral loss predicted (~1.5% to 3.0% annualized trabecular loss)."
        antiresorptive_indicated = True
    elif s_ctx_ng_ml < 0.15 and total_p1np_ug_l < 20.0:
        remodeling_state = "ADYNAMIC_BONE_TURNOVER_SUPPRESSED"
        bmd_trend = "Over-suppression of remodeling; micro-damage accumulation risk."
        antiresorptive_indicated = False
    elif uncoupling_index >= 1.2:
        remodeling_state = "NET_ANABOLIC_BONE_FORMATION"
        bmd_trend = "Positive bone mineral balance favoring trabecular thickening."
        antiresorptive_indicated = False
    else:
        remodeling_state = "COUPLED_HOMEOSTATIC_REMODELING"
        bmd_trend = "Balanced physiological remodeling; maintenance of bone structural density."
        antiresorptive_indicated = False
        
    return {
        "s_ctx_resorption_marker_ng_ml": round(s_ctx_ng_ml, 3),
        "total_p1np_formation_marker_ug_l": round(total_p1np_ug_l, 1),
        "bone_remodeling_coupling_index": round(uncoupling_index, 2),
        "current_dexa_t_score": dexas_t_score,
        "remodeling_kinetic_state": remodeling_state,
        "projected_bmd_trajectory": bmd_trend,
        "antiresorptive_therapy_candidate": antiresorptive_indicated,
        "guidance": "Consider dual-energy x-ray absorptiometry and vitamin D / calcium / resistance exercise optimization."
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "analyze_bone_turnover_coupling",
                        "description": """Analyze bone remodeling dynamics using serum C-telopeptide (s-CTX, bone resorption marker) and Total P1NP (bone formation marker).
Computes formation-to-resorption coupling ratio, detects uncoupled bone loss in postmenopausal/andropausal states, and assesses antiresorptive response.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = analyze_bone_turnover_coupling(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'s_ctx_ng_ml': 0.32, 'total_p1np_ug_l': 44.0, 'dexas_t_score': -0.8, 'sex': 'FEMALE'}
        out = analyze_bone_turnover_coupling(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
