""" rippleHistory.shared.lib.ledgerChain.py

    This module keeps track of linked chains of ledgers, allowing us to
    efficiently skip ledgers that have already been processed.
"""
#############################################################################

class LedgerChain(object):
    """ This object keeps track of "chains" of ledgers.
    """
    def __init__(self):
        """ Standard initialiser.
        """
        self.chains = [] # List of contiguous chains of ledgers.  Each list
                         # item is a dictionary with the following entries:
                         #
                         #     'first_parent'
                         #
                         #        The ledger hash for the parent of the first
                         #        ledger in this chain.
                         #
                         #    'first_ledger'
                         #
                         #        The ledger hash for the first ledger in this
                         #        chain.
                         #
                         #     'last_ledger'
                         #
                         #         The ledger hash for the last ledger in this
                         #         chain.
                         #
                         #     'num_ledgers'
                         #
                         #         The number of ledgers in this chain.


    def add(self, ledger_hash, parent_hash):
        """ Add a ledger to the chain.

            'ledger_hash' is the unique hash value identifying this ledger, and
            'parent_hash' is the hash value for this ledger's parent (ie, the
            previous ledger in the chain).
        """
        connects_to_start = None # Ledger preceeds this chain in the list.
        connects_to_end   = None # Ledger follows this chain in the list.

        for chain_index,chain in enumerate(self.chains):
            if parent_hash == chain['last_ledger']:
                # The ledger connects to the end of this chain.
                connects_to_end = chain_index
            elif ledger_hash == chain['first_parent']:
                # The ledger connects to the start of this chain.
                connects_to_start = chain_index

        # Add this ledger onto the chain(s) it connects with, if any.

        if connects_to_start != None and connects_to_end != None:
            # This ledger connects to two chains -> combine them.
            chain1 = self.chains[connects_to_end]
            chain2 = self.chains[connects_to_start]

            new_chain = {'first_parent' : chain1['first_parent'],
                         'first_ledger' : chain1['first_ledger'],
                         'last_ledger'  : chain2['last_ledger'],
                         'num_ledgers'  : chain1['num_ledgers'] +
                                          chain2['num_ledgers'] + 1}

            self.chains.remove(chain1)
            self.chains.remove(chain2)
            self.chains.append(new_chain)
        elif connects_to_start != None:
            # This ledger connects to the start of a chain -> add it to the
            # start of the chain.
            chain = self.chains[connects_to_start]
            chain['first_parent'] = parent_hash
            chain['first_ledger'] = ledger_hash
            chain['num_ledgers']  = chain['num_ledgers'] + 1
        elif connects_to_end != None:
            # This ledger connets to the end of a chain -> add it to the end of
            # the chain.
            chain = self.chains[connects_to_end]
            chain['last_ledger'] = ledger_hash
            chain['num_ledgers'] = chain['num_ledgers'] + 1
        else:
            # This ledger doesn't connect to any existing chain -> create a new
            # chain just for this ledger.
            new_chain = {'first_parent' : parent_hash,
                         'first_ledger' : ledger_hash,
                         'last_ledger'  : ledger_hash,
                         'num_ledgers'  : 1}
            self.chains.append(new_chain)


    def get_chains(self):
        """ Return a list of the ledger chains.

            We return a list of ledger chains, where each chain represents a
            contiguous set of ledgers which have been added to this LedgerChain
            object.  Each list item is a dictionary with the following entries:

                'first_parent'
                
                    The ledger hash for the parent of the first ledger in this
                    chain.

                'first_ledger'

                    The ledger hash for the first ledger in this chain.

                'last_ledger'

                    The ledger hash for the last ledger in this chain.

                'num_ledgers'

                    The number of ledgers in this chain.
        """
        return self.chains

#############################################################################
#                                                                           #
#                           T E S T I N G   C O D E                         #
#                                                                           #
#############################################################################
#
#import random
#
#NUM_LEDGERS = 1000
#
#############################################################################
#
#def test():
#    """ Test out the ledger chain.
#    """
#    global next_ledger_num
#    next_ledger_num = 1
#
    # Start by building a linked list of ledgers.  Each ledger has a random
    # string of letters as the "key".
#
#    ledgers = [] # A list of ledgers.  Each list entry is a dictionary with the
                 # following entries:
                 #
                 #   'ledger_hash'
                 #
                 #       The random string that identifies this ledger.
                 #
                 #   'parent_hash'
                 #
                 #       The random string that identifies this ledger's parent
                 #       ledger.
#
#    ledger_index = {} # Maps ledger hash value to index into 'ledgers'.
#
#    prev_hash = None
#    for i in range(NUM_LEDGERS):
#        ledger_hash = get_random_hash()
#
#        ledger = {'ledger_hash' : ledger_hash,
#                  'parent_hash' : prev_hash}
#
#        ledgers.append(ledger)
#        ledger_index[ledger_hash] = len(ledgers)-1
#
#        prev_hash = ledger_hash
#
    # Testing: show the ledgers.
#
#    print
#    print "Ledgers:"
#    print
#    for ledger_hash in sorted(ledger_index.keys()):
#        ledger = ledgers[ledger_index[ledger_hash]]
#
#        print "  hash: %s, parent: %s" % (ledger['ledger_hash'],
#                                          ledger['parent_hash'])
#
#    print
#
    # We now want to process the ledgers at random, building our own set of
    # "ledger runs" that get joined together as necesssary.
#
#    ledger_chain = LedgerChain()
#
#    random_ledgers = ledger_index.keys()
#    random.shuffle(random_ledgers)
#
#    for ledger_hash in random_ledgers:
#        ledger = ledgers[ledger_index[ledger_hash]]
#
#        ledger_chain.add(ledger['ledger_hash'], ledger['parent_hash'])
#
    # Finally, display the ledger chains.
#
#    print
#    print "Ledger chains:"
#    print
#    tot = 0
#    for chain in ledger_chain.get_chains():
#        print "  %s..%s (%d ledgers)" % (chain['first_ledger'],
#                                         chain['last_ledger'],
#                                         chain['num_ledgers'])
#        tot = tot + chain['num_ledgers']
#    print
#    print tot
#
#############################################################################
#
#def get_random_hash():
#    """ Return a random hash value to use for a ledger.
#    """
#    global next_ledger_num
#    ledger_num = next_ledger_num
#    next_ledger_num = next_ledger_num + 1
#    return "LEDGER-%04d" % ledger_num
#
#    return uuid.uuid4().hex
#
#############################################################################
#
#if __name__ == "__main__":
#    test()

