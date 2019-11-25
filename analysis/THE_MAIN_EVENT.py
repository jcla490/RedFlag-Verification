from verification_funcs import VerifySkill

FIRES_PATH = 'data/Fires_Northwest.json'
RFWS_PATH = 'data/RFWs_Northwest.json'

verify = VerifySkill(RFWS_PATH, FIRES_PATH)

verify.query_params(20060101, 20151231, perc_size=80, cause='lightning')

# verify.forecast_skill_scores()
# verify.climo_skill_scores()
verify.gen_skill_scores()

print(verify.SKILL_DICT)
