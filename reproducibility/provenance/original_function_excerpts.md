# Original function excerpts

Static, line-numbered source evidence. These excerpts are never imported or executed.

## scripts/08_apply_refined_best_params.py::safe_str (original lines 57-60)

```text
57: def safe_str(x):
58:     if pd.isna(x):
59:         return ""
60:     return str(x)
```

## scripts/08_apply_refined_best_params.py::contains_any (original lines 63-65)

```text
63: def contains_any(text, keywords):
64:     text = safe_str(text)
65:     return any(k in text for k in keywords)
```

## scripts/08_apply_refined_best_params.py::level_to_numeric (original lines 68-104)

```text
68: def level_to_numeric(level):
69:     mapping = {
70:         "none": 0.0,
71:         "low": 0.25,
72:         "medium": 0.50,
73:         "high": 0.75,
74:         "raw": 1.0,
75:         "full": 1.0,
76: 
77:         "summary": 0.50,
78:         "hashed": 0.50,
79:         "did": 1.0,
80: 
81:         "single_point": 0.75,
82:         "region": 0.25,
83:         "accident_window": 0.75,
84:         "full_trip": 1.0,
85: 
86:         "raw_edr": 1.0,
87:         "event_summary": 0.50,
88: 
89:         "raw_video": 1.0,
90:         "raw_radar": 1.0,
91: 
92:         "injury_summary": 0.75,
93:         "injury_detail": 1.0,
94: 
95:         "liability_summary": 0.75,
96:         "liability_detail": 1.0,
97: 
98:         "policy_hash": 0.50,
99:         "policy_relation": 0.75,
100: 
101:         "claim_range": 0.50,
102:         "claim_exact": 0.75,
103:     }
104:     return mapping.get(safe_str(level), 0.0)
```

## scripts/08_apply_refined_best_params.py::compute_A (original lines 143-163)

```text
143: def compute_A(row):
144:     values = []
145: 
146:     severity = row.get("collision_severity", None)
147: 
148:     if severity == 1:
149:         values.append(1.0)
150:     elif severity == 2:
151:         values.append(0.75)
152:     elif severity == 3:
153:         values.append(0.25)
154:     else:
155:         values.append(0.25)
156: 
157:     values.append(level_to_numeric(row.get("content_injury_info_level", "none")))
158:     values.append(level_to_numeric(row.get("content_liability_info_level", "none")))
159:     values.append(level_to_numeric(row.get("content_edr_data_level", "none")))
160:     values.append(level_to_numeric(row.get("content_video_data_level", "none")))
161:     values.append(level_to_numeric(row.get("content_radar_data_level", "none")))
162: 
163:     return max(values)
```

## scripts/08_apply_refined_best_params.py::compute_Iv (original lines 166-181)

```text
166: def compute_Iv(row):
167:     values = []
168: 
169:     values.append(level_to_numeric(row.get("content_driver_identity_level", "none")))
170:     values.append(level_to_numeric(row.get("content_vehicle_identity_level", "none")))
171:     values.append(level_to_numeric(row.get("content_policy_info_level", "none")))
172:     values.append(level_to_numeric(row.get("content_location_granularity", "none")))
173:     values.append(level_to_numeric(row.get("content_trajectory_granularity", "none")))
174: 
175:     if row.get("content_has_driver_did", 0) == 1:
176:         values.append(1.0)
177: 
178:     if row.get("content_has_vehicle_did", 0) == 1:
179:         values.append(1.0)
180: 
181:     return max(values)
```

## scripts/08_apply_refined_best_params.py::compute_Ha (original lines 184-206)

```text
184: def compute_Ha(row):
185:     values = []
186: 
187:     severity = row.get("collision_severity", None)
188: 
189:     if severity == 1:
190:         values.append(1.0)
191:     elif severity == 2:
192:         values.append(0.75)
193:     elif severity == 3:
194:         values.append(0.25)
195:     else:
196:         values.append(0.25)
197: 
198:     values.append(level_to_numeric(row.get("content_injury_info_level", "none")))
199:     values.append(level_to_numeric(row.get("content_liability_info_level", "none")))
200:     values.append(level_to_numeric(row.get("content_claim_amount_level", "none")))
201:     values.append(level_to_numeric(row.get("content_trajectory_granularity", "none")))
202:     values.append(level_to_numeric(row.get("content_edr_data_level", "none")))
203:     values.append(level_to_numeric(row.get("content_video_data_level", "none")))
204:     values.append(level_to_numeric(row.get("content_radar_data_level", "none")))
205: 
206:     return max(values)
```

## scripts/08_apply_refined_best_params.py::compute_Rl_content (original lines 209-238)

```text
209: def compute_Rl_content(row):
210:     values = []
211: 
212:     severity = row.get("collision_severity", None)
213: 
214:     if severity == 1:
215:         values.append(1.0)
216:     elif severity == 2:
217:         values.append(0.75)
218:     else:
219:         values.append(0.25)
220: 
221:     police_attend = row.get("did_police_officer_attend_scene_of_accident", None)
222: 
223:     if police_attend == 1:
224:         values.append(0.75)
225: 
226:     if row.get("content_has_raw_edr", 0) == 1:
227:         values.append(1.0)
228: 
229:     if row.get("content_has_camera_video", 0) == 1:
230:         values.append(0.75)
231: 
232:     if row.get("content_has_radar_data", 0) == 1:
233:         values.append(0.75)
234: 
235:     values.append(level_to_numeric(row.get("content_liability_info_level", "none")))
236:     values.append(level_to_numeric(row.get("content_injury_info_level", "none")))
237: 
238:     return max(values) if values else 0.0
```

## scripts/08_apply_refined_best_params.py::get_high_floor_mask (original lines 241-271)

```text
241: def get_high_floor_mask(df):
242:     """
243:     强敏感兜底规则。
244:     与 07b 保持一致。
245:     """
246:     mask = pd.Series([False] * len(df), index=df.index)
247: 
248:     mask = mask | (df["collision_severity"] == 1)
249: 
250:     if "content_has_raw_edr" in df.columns:
251:         mask = mask | (df["content_has_raw_edr"] == 1)
252: 
253:     if "content_trajectory_granularity" in df.columns:
254:         mask = mask | (df["content_trajectory_granularity"].astype(str) == "full_trip")
255: 
256:     if "content_edr_data_level" in df.columns:
257:         mask = mask | (df["content_edr_data_level"].astype(str).isin(["raw", "raw_edr"]))
258: 
259:     if "content_video_data_level" in df.columns:
260:         mask = mask | (df["content_video_data_level"].astype(str) == "raw_video")
261: 
262:     if "content_radar_data_level" in df.columns:
263:         mask = mask | (df["content_radar_data_level"].astype(str) == "raw_radar")
264: 
265:     if "content_injury_info_level" in df.columns:
266:         mask = mask | (df["content_injury_info_level"].astype(str) == "injury_detail")
267: 
268:     if "content_liability_info_level" in df.columns:
269:         mask = mask | (df["content_liability_info_level"].astype(str) == "liability_detail")
270: 
271:     return mask
```

## scripts/08_apply_refined_best_params.py::compute_ptf_subfactors (original lines 280-629)

```text
280: def compute_ptf_subfactors(row):
281:     """
282:     返回五个 PTFa 子因子：
283:     role_claim
284:     relation_claim
285:     qualification_claim
286:     regulator_claim
287:     court_claim
288: 
289:     说明：
290:     这些值表示访问策略分支触发的证明要求强度，
291:     不是消费者明文隐私属性。
292: 
293:     当前实验中：
294:     - access_required_claims 是 required_claim_types 在 CSV 中的落地字段；
295:     - access_allowed_roles 是访问策略允许角色，不是消费者明文角色；
296:     - access_usage_purpose 是访问用途/策略上下文；
297:     - access_task_type 是访问任务类型；
298:     - 执法、监管、法院授权字段是显式强证明触发标志。
299: 
300:     子因子采用 0 / 0.5 / 0.75 / 1 四档：
301:     - 0：不触发该类证明；
302:     - 0.5：普通角色/机构身份类证明；
303:     - 0.75：任务或用途间接触发的中强度证明；
304:     - 1：策略字段显式要求的强证明。
305:     """
306:     allowed_roles = safe_str(row.get("access_allowed_roles", ""))
307:     required_claims = safe_str(row.get("access_required_claims", ""))
308:     usage_purpose = safe_str(row.get("access_usage_purpose", ""))
309:     task_type = safe_str(row.get("access_task_type", ""))
310: 
311:     # 合并文本，便于识别中文/英文关键词
312:     all_text = "|".join([
313:         allowed_roles,
314:         required_claims,
315:         usage_purpose,
316:         task_type
317:     ])
318: 
319:     role_claim = 0.0
320:     relation_claim = 0.0
321:     qualification_claim = 0.0
322:     regulator_claim = 0.0
323:     court_claim = 0.0
324: 
325:     # =========================================================
326:     # 1. 角色/机构身份证明 role_claim
327:     # =========================================================
328:     # 普通机构/业务角色：0.5
329:     if contains_any(
330:         all_text,
331:         [
332:             # English
333:             "researcher",
334:             "research_institution",
335:             "insurance_company",
336:             "repair_shop",
337:             "vehicle_owner",
338:             "platform_auditor",
339:             "auditor",
340:             "business_analyst",
341:             "organization_identity",
342:             "institution_identity",
343:             "role_claim",
344: 
345:             # Chinese
346:             "研究机构",
347:             "授权研究机构",
348:             "保险公司",
349:             "保险机构",
350:             "维修机构",
351:             "维修企业",
352:             "车主",
353:             "车辆所有者",
354:             "平台审核员",
355:             "审核员",
356:             "业务分析员",
357:             "机构身份",
358:             "平台审核身份",
359:             "角色证明",
360:             "身份认证",
361:             "身份声明",
362:         ]
363:     ):
364:         role_claim = max(role_claim, 0.5)
365: 
366:     # 监管/执法/司法角色：1.0
367:     if contains_any(
368:         all_text,
369:         [
370:             # English
371:             "traffic_police",
372:             "police",
373:             "regulator",
374:             "court",
375:             "judicial_authority",
376:             "law_enforcement",
377:             "supervisor",
378: 
379:             # Chinese
380:             "交警",
381:             "交通警察",
382:             "执法",
383:             "执法机构",
384:             "监管",
385:             "监管机构",
386:             "法院",
387:             "司法",
388:             "司法机关",
389:             "审计机关",
390:         ]
391:     ):
392:         role_claim = max(role_claim, 1.0)
393: 
394:     # =========================================================
395:     # 2. 关系证明 relation_claim
396:     # =========================================================
397:     # required_claims 显式要求关系证明：1.0
398:     if contains_any(
399:         required_claims,
400:         [
401:             # English
402:             "policy_relation",
403:             "vehicle_owner_relation",
404:             "accident_related_relation",
405:             "case_relation",
406:             "business_relation",
407:             "claim_relation",
408:             "relation_claim",
409: 
410:             # Chinese
411:             "保单关系",
412:             "车辆关系",
413:             "车主关系",
414:             "事故关系",
415:             "事故关联",
416:             "案件关系",
417:             "业务关系",
418:             "理赔关系",
419:             "关系证明",
420:         ]
421:     ):
422:         relation_claim = max(relation_claim, 1.0)
423: 
424:     # 任务间接触发关系证明：0.75
425:     elif contains_any(
426:         task_type,
427:         [
428:             "claim_review",
429:             "repair_assessment",
430:             "accident_recheck",
431:             "insurance_claim",
432:             "case_review",
433:             "理赔审核",
434:             "维修评估",
435:             "事故复核",
436:             "保险理赔",
437:             "案件复核",
438:         ]
439:     ):
440:         relation_claim = max(relation_claim, 0.75)
441: 
442:     # 用途间接触发关系证明：0.75
443:     if contains_any(
444:         usage_purpose,
445:         [
446:             "claim",
447:             "repair",
448:             "case",
449:             "事故复核",
450:             "理赔",
451:             "维修",
452:             "案件",
453:         ]
454:     ):
455:         relation_claim = max(relation_claim, 0.75)
456: 
457:     # =========================================================
458:     # 3. 资质/用途批准证明 qualification_claim
459:     # =========================================================
460:     # required_claims 显式要求资质证明：1.0
461:     if contains_any(
462:         required_claims,
463:         [
464:             # English
465:             "claim_adjuster_qualification",
466:             "accident_investigator_qualification",
467:             "judicial_appraisal_qualification",
468:             "repair_assessment_qualification",
469:             "research_approval",
470:             "usage_approval",
471:             "qualification_claim",
472: 
473:             # Chinese
474:             "理赔员资质",
475:             "理赔审核资质",
476:             "事故调查资质",
477:             "事故鉴定资质",
478:             "司法鉴定资质",
479:             "维修评估资质",
480:             "研究用途批准",
481:             "用途批准",
482:             "资质证明",
483:             "资格证明",
484:         ]
485:     ):
486:         qualification_claim = max(qualification_claim, 1.0)
487: 
488:     # 用途/任务间接触发资质或用途批准：0.75
489:     if contains_any(
490:         usage_purpose,
491:         [
492:             # English
493:             "claim",
494:             "repair",
495:             "investigation",
496:             "audit",
497:             "research",
498:             "business_statistics",
499:             "trend_research",
500:             "analysis",
501: 
502:             # Chinese
503:             "理赔",
504:             "维修",
505:             "调查",
506:             "审计",
507:             "研究",
508:             "趋势研究",
509:             "脱敏事故趋势研究",
510:             "事故业务统计",
511:             "业务统计",
512:             "统计分析",
513:             "业务分析",
514:         ]
515:     ):
516:         qualification_claim = max(qualification_claim, 0.75)
517: 
518:     if contains_any(
519:         task_type,
520:         [
521:             # English
522:             "research_analysis",
523:             "business_analysis",
524:             "claim_review",
525:             "repair_assessment",
526:             "accident_recheck",
527: 
528:             # Chinese
529:             "研究分析",
530:             "业务分析",
531:             "理赔审核",
532:             "维修评估",
533:             "事故复核",
534:         ]
535:     ):
536:         qualification_claim = max(qualification_claim, 0.75)
537: 
538:     # =========================================================
539:     # 4. 监管/执法证明 regulator_claim
540:     # =========================================================
541:     if row.get("access_law_enforcement_required", 0) == 1:
542:         regulator_claim = max(regulator_claim, 1.0)
543: 
544:     if row.get("access_regulatory_audit", 0) == 1:
545:         regulator_claim = max(regulator_claim, 1.0)
546: 
547:     if contains_any(
548:         all_text,
549:         [
550:             # English
551:             "traffic_police",
552:             "police",
553:             "regulator",
554:             "regulatory_audit",
555:             "law_enforcement",
556:             "audit",
557:             "supervision",
558:             "regulator_claim",
559: 
560:             # Chinese
561:             "交警",
562:             "交通警察",
563:             "监管",
564:             "监管审计",
565:             "执法",
566:             "执法调查",
567:             "审计",
568:             "监督",
569:             "监管证明",
570:             "执法证明",
571:         ]
572:     ):
573:         regulator_claim = max(regulator_claim, 0.75)
574: 
575:     if contains_any(
576:         task_type,
577:         [
578:             "law_enforcement",
579:             "regulatory_audit",
580:             "执法调查",
581:             "监管审计",
582:         ]
583:     ):
584:         regulator_claim = max(regulator_claim, 1.0)
585: 
586:     # =========================================================
587:     # 5. 法院/司法授权证明 court_claim
588:     # =========================================================
589:     if row.get("access_court_authorization_required", 0) == 1:
590:         court_claim = max(court_claim, 1.0)
591: 
592:     if contains_any(
593:         required_claims,
594:         [
595:             # English
596:             "court_authorization",
597:             "judicial_authorization",
598:             "judicial_warrant",
599:             "court_claim",
600: 
601:             # Chinese
602:             "法院授权",
603:             "司法授权",
604:             "司法许可",
605:             "法院许可",
606:             "法院授权证明",
607:             "司法授权证明",
608:         ]
609:     ):
610:         court_claim = max(court_claim, 1.0)
611: 
612:     if contains_any(
613:         task_type,
614:         [
615:             "judicial_investigation",
616:             "raw_evidence_access",
617:             "司法调查",
618:             "原始证据访问",
619:         ]
620:     ):
621:         court_claim = max(court_claim, 0.75)
622: 
623:     return pd.Series({
624:         "role_claim": role_claim,
625:         "relation_claim": relation_claim,
626:         "qualification_claim": qualification_claim,
627:         "regulator_claim": regulator_claim,
628:         "court_claim": court_claim
629:     })
```

## scripts/08b_apply_ptfa_v2_final_params.py::ptfa_to_level (original lines 203-214)

```text
203: def ptfa_to_level(score, low_th, high_th):
204:     """
205:     PTFa 分数转等级。
206:     与 07d 保持一致：
207:     score < low_th -> low
208:     low_th <= score < high_th -> medium
209:     score >= high_th -> high
210:     """
211:     result = pd.Series(["medium"] * len(score), index=score.index)
212:     result[score < low_th] = "low"
213:     result[score >= high_th] = "high"
214:     return result
```

## scripts/08b_apply_ptfa_v2_final_params.py::compute_required_auth_level_vectorized (original lines 217-263)

```text
217: def compute_required_auth_level_vectorized(df, base_level_col, ptf_level_col, output_scope_col):
218:     """
219:     与 07d 中 required_auth_level 规则保持一致。
220: 
221:     base_data_level_pred_refined + PTFa_level_final + output_scope -> required_auth_level_final
222:     """
223:     base = df[base_level_col].astype(str).map(normalize_label)
224:     ptf = df[ptf_level_col].astype(str).map(normalize_label)
225:     scope = df[output_scope_col].astype(str).map(normalize_label)
226: 
227:     result = pd.Series(["medium"] * len(df), index=df.index)
228: 
229:     # high 基础数据等级不能降级
230:     result[base == "high"] = "high"
231: 
232:     raw_mask = scope == "raw_evidence"
233: 
234:     # medium 数据请求 raw_evidence -> high
235:     result[(base == "medium") & raw_mask] = "high"
236: 
237:     # medium 数据非 raw_evidence -> medium
238:     result[(base == "medium") & (~raw_mask)] = "medium"
239: 
240:     # low 数据 + low PTFa + aggregate -> low
241:     result[(base == "low") & (ptf == "low") & (scope == "aggregate")] = "low"
242: 
243:     # low 数据 + low PTFa + masked/raw -> medium
244:     result[
245:         (base == "low")
246:         & (ptf == "low")
247:         & (scope.isin(["masked_record", "raw_evidence"]))
248:     ] = "medium"
249: 
250:     # low 数据 + medium PTFa -> medium
251:     result[(base == "low") & (ptf == "medium")] = "medium"
252: 
253:     # low 数据 + high PTFa + aggregate -> medium
254:     result[(base == "low") & (ptf == "high") & (scope == "aggregate")] = "medium"
255: 
256:     # low 数据 + high PTFa + masked/raw -> high
257:     result[
258:         (base == "low")
259:         & (ptf == "high")
260:         & (scope.isin(["masked_record", "raw_evidence"]))
261:     ] = "high"
262: 
263:     return result
```

## scripts/08b_apply_ptfa_v2_final_params.py::proof_mode_from_auth (original lines 266-272)

```text
266: def proof_mode_from_auth(auth_level):
267:     mapping = {
268:         "low": "basic",
269:         "medium": "medium",
270:         "high": "strong",
271:     }
272:     return auth_level.map(lambda x: mapping.get(str(x).strip().lower(), "medium"))
```

## scripts/08b_apply_ptfa_v2_final_params.py::apply_final_params (original lines 279-313)

```text
279: def apply_final_params(df, params):
280:     """
281:     应用 07d 的 PTFa V2 参数。
282: 
283:     注意：
284:     - 不重新计算 role_claim 等字段；
285:     - 直接使用 refined 数据中的 role_claim/relation_claim/...；
286:     - 输出 final 后缀字段。
287:     """
288:     df = df.copy()
289: 
290:     df["PTFa_final"] = (
291:         params["ptf_w_role"] * df["role_claim"]
292:         + params["ptf_w_relation"] * df["relation_claim"]
293:         + params["ptf_w_qualification"] * df["qualification_claim"]
294:         + params["ptf_w_regulator"] * df["regulator_claim"]
295:         + params["ptf_w_court"] * df["court_claim"]
296:     ).clip(upper=1.0)
297: 
298:     df["PTFa_level_final"] = ptfa_to_level(
299:         df["PTFa_final"],
300:         params["ptf_low_threshold"],
301:         params["ptf_high_threshold"]
302:     )
303: 
304:     df["required_auth_level_final"] = compute_required_auth_level_vectorized(
305:         df,
306:         "base_data_level_pred_refined",
307:         "PTFa_level_final",
308:         "output_scope"
309:     )
310: 
311:     df["proof_mode_final"] = proof_mode_from_auth(df["required_auth_level_final"])
312: 
313:     return df
```

## scripts/22_socc_phase2_policy_ablation.py::policy_full (original lines 171-182)

```text
171: def policy_full(base: pd.Series, ptfa: pd.Series, scope: pd.Series) -> pd.Series:
172:     """Final 08b policy expressed only with current semantic scope names."""
173:     result = pd.Series("medium", index=base.index, dtype="object")
174:     result[base == "high"] = "high"
175:     result[(base == "medium") & (scope == "raw_record")] = "high"
176:     result[(base == "medium") & (scope != "raw_record")] = "medium"
177:     result[(base == "low") & (ptfa == "low") & (scope == "summary_view")] = "low"
178:     result[(base == "low") & (ptfa == "low") & scope.isin(["masked_record", "raw_record"])] = "medium"
179:     result[(base == "low") & (ptfa == "medium")] = "medium"
180:     result[(base == "low") & (ptfa == "high") & (scope == "summary_view")] = "medium"
181:     result[(base == "low") & (ptfa == "high") & scope.isin(["masked_record", "raw_record"])] = "high"
182:     return result
```

## scripts/22_socc_phase2_policy_ablation.py::policy_without_ptfa (original lines 185-193)

```text
185: def policy_without_ptfa(base: pd.Series, scope: pd.Series) -> pd.Series:
186:     """PTFa is neither read nor allowed to raise authentication."""
187:     result = pd.Series("medium", index=base.index, dtype="object")
188:     result[base == "high"] = "high"
189:     result[(base == "medium") & (scope == "raw_record")] = "high"
190:     result[(base == "medium") & (scope != "raw_record")] = "medium"
191:     result[(base == "low") & (scope == "summary_view")] = "low"
192:     result[(base == "low") & scope.isin(["masked_record", "raw_record"])] = "medium"
193:     return result
```

## scripts/22_socc_phase2_policy_ablation.py::policy_without_output_scope (original lines 196-205)

```text
196: def policy_without_output_scope(base: pd.Series, ptfa: pd.Series) -> pd.Series:
197:     """Base + PTFa only; no output-scope value is read or substituted."""
198:     result = pd.Series("medium", index=base.index, dtype="object")
199:     result[base == "high"] = "high"
200:     result[(base == "medium") & (ptfa == "high")] = "high"
201:     result[(base == "medium") & (ptfa != "high")] = "medium"
202:     result[(base == "low") & (ptfa == "high")] = "high"
203:     result[(base == "low") & (ptfa == "medium")] = "medium"
204:     result[(base == "low") & (ptfa == "low")] = "low"
205:     return result
```

## scripts/26_socc_phase2_base_only_control.py::build_vm_counts (original lines 233-252)

```text
233: def build_vm_counts(base_only: pd.Series, full: pd.Series) -> pd.DataFrame:
234:     rows = []
235:     policies = {
236:         "base_only": count_modes(base_only),
237:         "full_policy": count_modes(full),
238:         "fixed_strong": {"Basic": 0, "Medium": 0, "Strong": EXPECTED_ROWS},
239:     }
240:     for policy, counts in policies.items():
241:         for mode in MODE_ORDER:
242:             rows.append(
243:                 {
244:                     "policy": policy,
245:                     "proof_mode": mode,
246:                     "count": counts[mode],
247:                     "share": round(counts[mode] / EXPECTED_ROWS, 10),
248:                     "denominator": EXPECTED_ROWS,
249:                     "note": "Counts for downstream VM cost analysis; no cost model is applied here.",
250:                 }
251:             )
252:     return pd.DataFrame(rows)
```
