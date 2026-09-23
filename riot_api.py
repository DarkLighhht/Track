import base64, requests
class RiotAPIError(RuntimeError): pass
class RiotAPI:
    AUTH='https://auth.riotgames.com'; HOSTS={'americas':'https://americas.api.riotgames.com','europe':'https://europe.api.riotgames.com','asia':'https://asia.api.riotgames.com'}
    def __init__(self,client_id,client_secret,redirect_uri,region='europe'):
        self.client_id=client_id; self.client_secret=client_secret; self.redirect_uri=redirect_uri; self.region=region.lower()
        if self.region not in self.HOSTS: raise ValueError('RIOT_REGION: americas/europe/asia')
    def _basic(self): return base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
    def _token(self,data,action):
        if not self.client_id or not self.client_secret: raise RiotAPIError('RSO Client ID/Secret не настроены.')
        r=requests.post(f'{self.AUTH}/token',headers={'Authorization':f'Basic {self._basic()}','Content-Type':'application/x-www-form-urlencoded'},data=data,timeout=20); return self._json(r,action)
    def exchange_code(self,code): return self._token({'grant_type':'authorization_code','code':code,'redirect_uri':self.redirect_uri},'обмена authorization code')
    def refresh_access_token(self,refresh_token): return self._token({'grant_type':'refresh_token','refresh_token':refresh_token},'обновления access token')
    def get_account(self,token): return self._get('/riot/account/v1/accounts/me',token,'получения аккаунта')
    def get_matchlist(self,token,puuid): return self._get(f'/val/match/v1/matchlists/by-puuid/{puuid}',token,'получения истории матчей')
    def get_match(self,token,match_id): return self._get(f'/val/match/v1/matches/{match_id}',token,'получения матча')
    def _get(self,path,token,action): return self._json(requests.get(self.HOSTS[self.region]+path,headers={'Authorization':f'Bearer {token}'},timeout=20),action)
    @staticmethod
    def _json(r,action):
        if r.ok: return r.json()
        try: d=r.json()
        except ValueError: d=r.text[:500]
        raise RiotAPIError(f'{action}: HTTP {r.status_code}: {d}')
