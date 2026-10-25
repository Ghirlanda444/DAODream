(fn SetStamina (Pct Txt)
  (Avanzamento|SetPercent (Variabili|WBP_CombatHUD|OttieniStaminaBar) Pct)
  (Widget|SetText(Text) (Variabili|WBP_CombatHUD|OttieniStaminaLabel) (Utilità|Testo|ToText(String) Txt)))
