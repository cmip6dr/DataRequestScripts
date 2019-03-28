from utils_wb import workbook
import collections, json, time
from utils import *

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

class Review(object):
  def __init__(self):
    cc = collections.defaultdict( set )
    ccex0 = collections.defaultdict( set )
    ccex = collections.defaultdict( set )
    dq = dreq.loadDreq()
    mips = set( [i.label for i in dq.coll['mip'].items] )
    expts = set( [i.label for i in dq.coll['experiment'].items] )
    self.dq = dq
    collect.add( dq )
    self.fload()
    wb = workbook( 'AR6WG1_priorityVariables.xlsx' )
    sh = wb.book.sheet_by_name( 'AR6-WG1 Priority Variables' )
    for i in range(4,sh.nrows):
      a, b = [str(x.value) for x in sh.row(i)[1:3] ]
      if a.strip() != '':
        vars = [x.strip() for x in a.split( ',' )]
        for v in vars:
          cc[b].add( v )
        expt00 = str( sh.row(i)[5].value ).strip()
        expts00 = [x.strip() for x in expt00.split(',')]
        es = set()
        for e in expts00:
          if e in mips:
            for u in dq.inx.iref_by_sect[e].a['experiment']:
              es.add( dq.inx.uid[u].label )
          elif e in expts:
            es.add(e)
          else:
            print ('ERROR.expt: experiment not found: %s' % e )
        for v in vars:
          for e in es:
            ccex0[ (v,b) ].add( e )
        
    self.cmv = set()
    self.cmvu = set()
    for x in sorted( cc.keys() ):
      print ( "%s: %s" % (x, sorted( list( cc[x] ) ) ) )
      tables = self.ftab.get(  x, [] )
      if len(tables) == 0:
        print ('NO CMIP FREQUENCY FOUND FOR %s' % x ) 
      for v0 in cc[x]:
        v = v0
        if v.find('(') != -1:
          v = v[:v.find('(')].strip()
          print ('%s --> %s' % (v0,v))
        if v not in dq.coll['var'].items[0]._labelDict:
          print ('ERROR.001: not found: %s' % v )
        else:
          this = dq.coll['var'].items[0]._labelDict[v]
          lll = []
          for u in dq.inx.iref_by_sect[this.uid].a['CMORvar']:
            f = dq.inx.uid[u].frequency
            if f in tables:
              lll.append( dq.inx.uid[u] )
          if len(lll) == 0:
            print ('ERROR.lll: not found at this frequency: %s.%s' % (x,v) )
          else:
            print ('%s.%s: %s' % (x,v,[a.mipTable for a in lll]) )
            llltabs = set( [a.mipTable for a in lll] )
            for a in lll:
              if a.mipTable in ('Eday','CFday') and 'day' in llltabs:
                pass
              else:
                self.cmv.add(a)
                self.cmvu.add(a.uid)
                for e in ccex0[ (v,x) ]:
                  ccex[e].add( a.uid )
    self.ccex = ccex
               

  def query(self):
    self.sc = scope.dreqQuery( dq=self.dq )

    self.sc.gridPolicyDefaultNative = True
    self.sc.setTierMax( 3 )
    self.vol = collections.defaultdict( dict )
    self.vol2 = collections.defaultdict( dict )
    self.vol3 = collections.defaultdict( dict )

    ttlttl = 0
    oo = open( 'AR6WG1_priorityVariables_volumes.txt', 'w' )
    for k in self.ccex:
      v2 = collections.defaultdict( float )
      for i in self.dq.coll['requestVar'].items:
        if i.vid in self.ccex[k]:
          i.priority = 1
        else:
          i.priority = 4
      iex = self.dq.coll['experiment'].items[0]._labelDict[k]
      mip = iex.mip


      self.sc.exptFilter = set( [iex.uid,] )
      vs = volsum.vsum( self.sc, scope.odsz, scope.npy, odir='xls' )
    
      self.vs = vs
      vs.run( 'TOTAL', 'xls/requestVol_%s_1_1' % k , pmax=1, doxlsx=True )
      vsmode='full'
      vs.anal(olab='TOTAL',doUnique=False, mode=vsmode, makeTabs=True)
      for f in sorted( vs.res['vf'].keys() ):
           print ( 'Frequency: %s: %s' % (f, vs.res['vf'][f]*2.*1.e-12 ) )
           self.vol[k][f] = vs.res['vf'][f]*2.
      ttl = sum( [x for kk,x in vs.res['vu'].items()] )*2.*1.e-9
      for u,x in vs.res['vu'].items():
        v2[ self.dq.inx.uid[u].mipTable ] += x*2.*1.e-6
        self.vol3[k][ (self.dq.inx.uid[u].mipTable, self.dq.inx.uid[u].label )] = x*2.*1.e-9
      for t in v2:
        self.vol2[k][t] = v2[t]
      print( 'TOTAL volume: %s: %8.2fGB' % (k,ttl) )
      oo.write( 'TOTAL volume: %s: %8.2fGB\n' % (k,ttl) )
      ttlttl += ttl*1.e-3
    print( 'TOTAL volume: %8.2fTB' % ttlttl )
    oo.write( 'TOTAL volume: %8.2fTB\n' % ttlttl )
    oo.close()
   

  def jdump(self):

    oo = open( 'AR6WG1_priorityVariables_volumes.json', 'w' )
    info = {'source':'script ar6.py; sheet: AR6WG1_priorityVariables.xlsx; volume estimates in GB from dreqPy', 'author':'Martin Juckes (martin.juckes@stfc.ac.uk)', 'creation_date':time.ctime()}
    req = dict()
    uids = dict()
    for k in sorted( self.vol3.keys() ):
      cmv = collections.defaultdict( dict )
      this = dict()
      for t,v in self.vol3[k]:
        cmv[t][v] = self.vol3[k][(t,v)]
      for t in cmv.keys():
        this[t] = cmv[t]
      req[k] = this
      uids[k] = sorted( list( self.ccex[k] ) )
      
    json.dump( {'header':info, 'requested':req, 'uids':uids}, oo, indent=4, sort_keys=True )
    self.req01 = req

    oo = open( 'AR6WG1_priorityVariables.json', 'w' )
    info = {'source':'script ar6.py; sheet: AR6WG1_priorityVariables.xlsx', 'author':'Martin Juckes (martin.juckes@stfc.ac.uk)', 'creation_date':time.ctime()}
    req = dict()
    uids = dict()
    for k in sorted( self.ccex.keys() ):
      cmv = collections.defaultdict( set )
      this = dict()
      for u in self.ccex[k]:
        i = self.dq.inx.uid[u]
        cmv[i.mipTable].add(i.label)
      for t in cmv.keys():
        this[t] = sorted( list( cmv[t] ) )
      req[k] = this
      uids[k] = sorted( list( self.ccex[k] ) )
      
    json.dump( {'header':info, 'requested':req, 'uids':uids}, oo, indent=4, sort_keys=True )
    self.req = req

  def cmvdump(self):
    v0 = collections.defaultdict( float )
    v1 = collections.defaultdict( float )
    v2 = collections.defaultdict( float )
    ix = collections.defaultdict( set )
    for ex, dd in self.req01.items():
      for tab, dd1 in dd.items():
        for var, x in dd1.items():
          v0[(tab,var)] += x
          v1[tab] += x
          v2[ex] += x
          ix[tab].add(var)
    ks1 = sorted( v1.keys(), key=lambda x: v1[x], reverse=True )
    ks2 = sorted( v2.keys(), key=lambda x: v2[x], reverse=True )
    hh0 = ['','']
    hh1 = ['EXPERIMENT','TOTAL [TB]',]
    rows = collections.defaultdict( list )
    rows['TOTAL'].append('TOTAL [TB]' )
    rows['TOTAL'].append( '%6.3f' % sum( [v*1.e-3 for k,v in v2.items()] ) )
    for ex in ks2:
      rows[ex].append(ex)
      rows[ex].append('%6.3f' % (v2[ex]*1.e-3) )

    for tab in ks1:
      vx = dict()
      for var in ix[tab]:
        vx[var] = v0[(tab,var)]
      kv = sorted( vx.keys(), key=lambda x: vx[x], reverse=True )
      for var in kv:
        hh0.append( tab )
        hh1.append( var )
        ss = 0.
        for ex in ks2:
          if tab in self.req01[ex] and var in self.req01[ex][tab]:
            rows[ex].append( '%6.3f' % self.req01[ex][tab][var] )
            ss += self.req01[ex][tab][var]
          else:
            rows[ex].append( '' )
        if ss > 0.:
            rows['TOTAL'].append( '%6.3f' % (ss*1.e-3) )
        else:
            rows['TOTAL'].append( '' )
      
      
    oo = open( 'AR6WG1_priorityVariables_table.csv', 'w' )
    oo.write( '\t'.join( hh0 ) + '\n' )
    oo.write( '\t'.join( hh1 ) + '\n' )
    oo.write( '\t'.join( rows['TOTAL'] ) + '\n' )
    for ex in ks2:
      oo.write( '\t'.join( rows[ex] ) + '\n' )
    oo.close()
          

  def fload(self):
    e = json.load( open( 'frequency.json' ) )
    self.ftab = collections.defaultdict(set)
    for t,v in e['frequency'].items():
      for l in v[1:]:
        self.ftab[str(l)].add(t)
    print ( self.ftab.keys() )
        
r = Review()
r.query()
r.jdump()
r.cmvdump()
