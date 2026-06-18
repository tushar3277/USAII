import os
import json
import torch
import re
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

# =====================================================
# CONFIGURATION
# =====================================================

HF_TOKEN = "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"
MODEL_NAME = "google/gemma-2-2b-it"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR 

CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.jsonl")
BERT_FILE = os.path.join(DATA_DIR, "bert_synthetic_data.jsonl")

# Output File 1: Your original 1-to-1 target breakdown
OUTPUT_FILE_1TO1 = os.path.join(DATA_DIR, "oneToOne_conversations_dashboard_feed.jsonl")
# Output File 2: The brand new global macro sender profiles file
OUTPUT_FILE_GLOBAL = os.path.join(DATA_DIR, "global_sender_profiles.jsonl")

# =====================================================
# DEVICE CHECK
# =====================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("=" * 60)
print(f"Device: {DEVICE}")
if DEVICE == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))
print("=" * 60)

# =====================================================
# LOAD MODEL (Bfloat16 Execution optimization)
# =====================================================

print("Loading Gemma in native bfloat16 precision...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,   
    device_map="auto",
    attn_implementation="sdpa",    
    token=HF_TOKEN
)
model.eval()
print("Gemma loaded successfully. 🚀")

# =====================================================
# LOAD BERT LOOKUP TABLE
# =====================================================

print("Loading BERT risk profiles...")
bert_lookup = {}
if os.path.exists(BERT_FILE):
    with open(BERT_FILE, "r", encoding="utf-8") as bf:
        for line in bf:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                analysis = data.get("bert_analysis", {})
                sender_id = analysis.get("sender_id")
                if sender_id:
                    bert_lookup[sender_id] = analysis
            except Exception:
                continue
print(f"Loaded {len(bert_lookup)} sender profiles.")

# =====================================================
# SYSTEM PROMPTS (Strict Dynamic Logic Mapping)
# =====================================================

SYSTEM_PROMPT_1TO1 = """
You are an expert Trust & Safety Behavioral Profiler assisting an enterprise moderator.
Your job is to evaluate structured logs containing chronological user conversations paired with DeBERTa NLP weights.

CRITICAL INSTRUCTION FOR CALCULATING AI CONFIDENCE:
- Do NOT output a static placeholder like 0.92 or 0.99.
- Look directly at the provided 'risk-score' field inside the BERT multi-label scores. 
- You MUST dynamically calculate your 'ai_confidence_score' as a float between 0.00 and 1.00 based on how cleanly the chat text evidence aligns with that incoming BERT risk score.

Return ONLY valid JSON matching this schema:
{
  "behavioral_risk_pattern": "A concise 2-sentence summary.",
  "risk_category": "SEXTORTION_RISK | GROOMING_SEQUENCE | TARGETED_CYBERBULLYING | CREDIBLE_THREAT | COERCIVE_INTIMIDATION | HATE_SPEECH | TOXIC_BEHAVIOR | SEXUAL_HARASSMENT | DISMISS",
  "recommended_action": "TERMINATE_ALL_ACCOUNTS | IMMEDIATE_ACCOUNT_SUSPENSION | SHADOWBAN_USER | FORCE_DM_RESTRICTION | WARN_USER_STRICT | MONITOR_FURTHER | DISMISS",
  "analyst_alert_summary": "Technical moderation alert.",
  "ai_confidence_score": {current_bert_risk:.2f}
}
"""

SYSTEM_PROMPT_GLOBAL = """
You are an expert Trust & Safety Operations Supervisor compiling a macro offender dossier.
You are provided with a sender's global BERT matrix paired with a compilation summary of their infractions across ALL targeted unique victims.

CRITICAL INSTRUCTION FOR GLOBAL RISK SCORE:
- Do NOT use static placeholders.
- Mathematically calculate 'global_risk_score' as a float between 0.00 and 1.00. 
- Factor in multi-victim trends: if the sender repeats systematic predatory maneuvers (like grooming strings or extortion threats) across multiple unique targets, scale this value above 0.92.

Return ONLY valid JSON matching this schema:
{
  "global_behavioral_summary": "An overarching, multi-sentence macro summary of this platform user's behavioral patterns across all targets.",
  "primary_global_risk": "SEXTORTION_RISK | GROOMING_SEQUENCE | CROSS_PLATFORM_HARASSMENT | PREDATORY_RAPID_ESCALATION | MULTI_THREAT_CLUSTER | DISMISS",
  "final_corporate_action": "TERMINATE_ALL_ACCOUNTS | IMMEDIATE_ACCOUNT_SUSPENSION | SHADOWBAN_USER | WARN_AND_MONITOR | DISMISS",
  "cross_target_escalation_detected": true,
  "global_risk_score": 0.0
}
"""

# =====================================================
# EXTRACTOR GENERATION HELPER
# =====================================================

def query_gemma_json(prompt_text, system_context, max_tokens=350):
    gemma_prompt = f"<start_of_turn>user\n{system_context}\n\n{prompt_text}<end_of_turn>\n<start_of_turn>model\n"
    inputs = tokenizer(gemma_prompt, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,      # ENABLED SAMPLING: Allows the model mathematical variation to output custom floats
            temperature=0.1,     # Low temperature maintains strict formatting safety
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
        
    generated_tokens = outputs[0, inputs["input_ids"].shape[1]:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
    
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()
        
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    if start_idx != -1 and end_idx != -1:
        response_text = response_text[start_idx:end_idx + 1]
    response_text = response_text.replace("\n", " ").replace("\r", "")
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        fixed_text = re.sub(r'":\s*"([^"]*)"', lambda m: '": "' + m.group(1).replace('"', '\\"') + '"', response_text)
        return json.loads(fixed_text)

# =====================================================
# FILE INGESTION AND AGGREGATION LOOKUP PASS
# =====================================================

processed_count = 0
skipped_count = 0

# In-memory accumulator store to hold aggregated data needed for generating file 2 later
global_sender_aggregation_cache = {}

print("Starting One-to-One Analysis Pass...")

with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE_1TO1, "w", encoding="utf-8") as outfile:

    for line in infile:
        if not line.strip(): continue
        try:
            record = json.loads(line)
        except Exception:
            continue

        sender_id = record.get("sender_id")
        targets = record.get("targets", [])

        sender_bert = bert_lookup.get(
            sender_id,
            {
                "toxicity": 0.05, "bullying": 0.05, "threat": 0.05, "sexual": 0.05,
                "grooming": 0.05, "sextortion": 0.05, "coercion": 0.05, "hate": 0.05, "risk-score": 0.05
            }
        )

        if sender_bert.get("risk-score", 0) < 0.20:
            skipped_count += 1
            continue

        # Initialize this sender in our macro cache store if not already present
        if sender_id not in global_sender_aggregation_cache:
            global_sender_aggregation_cache[sender_id] = {
                "sender_id": sender_id,
                "master_bert_scores": sender_bert,
                "all_compiled_conversations": [],
                "target_evaluation_summaries": []
            }

        for target in targets:
            receiver_id = target.get("receiver_id")
            chat_history = target.get("conversation", [])

            paired_analysis = {
                "receiver_id": receiver_id,
                "sender_id": sender_id,
                "toxicity": sender_bert.get("toxicity"),
                "bullying": sender_bert.get("bullying"),
                "threat": sender_bert.get("threat"),
                "sexual": sender_bert.get("sexual"),
                "grooming": sender_bert.get("grooming"),
                "sextortion": sender_bert.get("sextortion"),
                "coercion": sender_bert.get("coercion"),
                "hate": sender_bert.get("hate"),
                "risk-score": sender_bert.get("risk-score"), # Injected direct tracking payload visibility
                "model_used": "deberta-v3-large",
                # "confidence": 0.91
            }

            output_dossier = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "conversation": chat_history,
                "bert_analysis": paired_analysis
            }

            user_prompt = (
                "Evaluate this relationship risk index dossier:\n\n"
                f"Sender ID: {sender_id}\n"
                f"Receiver ID: {receiver_id}\n"
                f"BERT multi-label scores: {json.dumps(paired_analysis)}\n"
                f"Chat History Text Content: {[msg.get('text', '') for msg in chat_history]}"
            )

            try:
                llm_advice = query_gemma_json(user_prompt, SYSTEM_PROMPT_1TO1)
            except Exception as e:
                # Armored taxonomy-mapped safe fallback engine
                fallback_risk = "DISMISS"
                lower_resp = str(e).lower()
                if "grooming" in lower_resp: fallback_risk = "GROOMING_SEQUENCE"
                elif "bullying" in lower_resp: fallback_risk = "TARGETED_CYBERBULLYING"
                elif "sextortion" in lower_resp: fallback_risk = "SEXTORTION_RISK"
                
                llm_advice = {
                    "behavioral_risk_pattern": "Automated pipeline parsing exception occurred.",
                    "risk_category": fallback_risk,
                    "recommended_action": "MONITOR_FURTHER" if fallback_risk != "DISMISS" else "DISMISS",
                    "analyst_alert_summary": f"Parse Failure: {str(e)}",
                    "ai_confidence_score": float(sender_bert.get("risk-score", 0.50))
                }

            output_dossier["llm_copilot_advice"] = llm_advice
            outfile.write(json.dumps(output_dossier, ensure_ascii=False) + "\n")
            processed_count += 1
            print(f"Processed 1to1 Target Records: {processed_count}", end="\r")

            # Store snippets cleanly into global memory loop block for Pass 2 processing
            global_sender_aggregation_cache[sender_id]["all_compiled_conversations"].extend([
                f"To {receiver_id}: {msg.get('text', '')}" for msg in chat_history
            ])
            global_sender_aggregation_cache[sender_id]["target_evaluation_summaries"].append({
                "target_id": receiver_id,
                "risk_category": llm_advice.get("risk_category"),
                "pattern_found": llm_advice.get("behavioral_risk_pattern")
            })

print("\n✔ One-to-One processing complete. Starting Aggregated Global Pass...")

# =====================================================
# PASS 2: GENERATION OF GLOBAL OFFENDER PROFILES FILE
# =====================================================
global_processed_count = 0

with open(OUTPUT_FILE_GLOBAL, "w", encoding="utf-8") as global_outfile:
    for sender_id, cached_payload in global_sender_aggregation_cache.items():
        
        macro_prompt = (
            f"Generate global synthesis for Sender Account: {sender_id}\n"
            f"Baseline Platform Threat Metrics: {json.dumps(cached_payload['master_bert_scores'])}\n"
            f"Target Evaluation Breakdowns: {json.dumps(cached_payload['target_evaluation_summaries'])}\n"
            f"Full Combined Platform Text Log: {cached_payload['all_compiled_conversations'][:40]}" # Slice bounds protect context windows
        )
        
        try:
            global_advice = query_gemma_json(macro_prompt, SYSTEM_PROMPT_GLOBAL, max_tokens=400)
        except Exception as e:
            global_advice = {
                "global_behavioral_summary": "Failed to compile clean structural evaluation profile.",
                "primary_global_risk": "MULTI_THREAT_CLUSTER",
                "final_corporate_action": "IMMEDIATE_ACCOUNT_SUSPENSION",
                "cross_target_escalation_detected": True,
                "global_risk_score": float(cached_payload['master_bert_scores'].get("risk-score", 0.75))
            }
            
        final_global_dossier = {
            "sender_id": sender_id,
            "overall_bert_profile": cached_payload['master_bert_scores'],
            "global_llm_supervisor_analysis": global_advice
        }
        
        global_outfile.write(json.dumps(final_global_dossier, ensure_ascii=False) + "\n")
        global_processed_count += 1
        print(f"Generated Aggregated Global Profiles: {global_processed_count}", end="\r")

print("\n")
print("=" * 60)
print("ALL PIPELINES COMPLETE")
print("=" * 60)
print(f"1-to-1 Targets Written    : {processed_count} -> {OUTPUT_FILE_1TO1}")
print(f"Global Profiles Written   : {global_processed_count} -> {OUTPUT_FILE_GLOBAL}")
print(f"Skipped Under Threshold   : {skipped_count}")
print("=" * 60)