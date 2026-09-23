from collections import Counter
def build_dashboard(riot,token,puuid,limit=10):
    history=riot.get_matchlist(token,puuid).get('history',[])[:limit]; matches=[]; k=d=a=w=n=0; agents=Counter(); maps=Counter()
    for x in history:
        mid=x.get('matchId')
        if not mid: continue
        try: m=riot.get_match(token,mid)
        except Exception: continue
        me=next((p for p in m.get('players',[]) if p.get('puuid')==puuid),None)
        if not me: continue
        s=me.get('stats') or {}; kk=int(s.get('kills',0)); dd=int(s.get('deaths',0)); aa=int(s.get('assists',0)); team=me.get('teamId'); winteam=next((t.get('teamId') for t in m.get('teams',[]) if t.get('won') is True),None); won=bool(winteam and team==winteam)
        k+=kk; d+=dd; a+=aa; n+=1; w+=won; agent=me.get('characterName') or 'Unknown'; mapid=m.get('matchInfo',{}).get('mapId','Unknown'); agents[agent]+=1; maps[mapid]+=1
        matches.append({'map':mapid,'mode':m.get('matchInfo',{}).get('gameMode','Unknown'),'agent':agent,'kills':kk,'deaths':dd,'assists':aa,'won':won})
    return {'matches':matches,'summary':{'matches':n,'wins':w,'losses':max(n-w,0),'kills':k,'deaths':d,'assists':a,'kd':round(k/max(d,1),2),'win_rate':round(w/n*100,1) if n else 0},'agents':agents.most_common(),'maps':maps.most_common()}
