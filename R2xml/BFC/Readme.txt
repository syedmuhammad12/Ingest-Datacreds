EU BFC Readme 2.4
======================

What's New in 2.4 R3 to R2 conversions
-------------------------------------
- Bug fix for downgrade-b1.xsl - B.1.8a and B.1.10.8a Name of drug not allways populated


Updates in 2.3 R3 to R2 conversions
-------------------------------------

- Bug fix for downgrade-a1.xsl - A.1.11 Other case identifiers in previous transmissions, fix seriousness flags for boolean "false" value
- Addition of code to allow N.2.r.2 to be copied into A.3.2.1 for NCA rerouted R3 files. downgrade-a3.xsl 
- Addition of variable in OID.xsl to allow the choice to keep original sender ID when converting to R2	
- Addition of code to handle UCUM dosage units that are not mapped to R2 codes. downgrade-b4.xsl 


Setting Variables in OID.xsl file
-------------------------------------

1. Option to use the reclassified XEVMPD medicinal product name when available

The R3 files may contain the medicinal products reclassified against the XEVMPD as well as the original verbatim term. Organisations wish to use the XEVMPD term rather than the verbatim term in the converted R2 file can so by setting the variable [XEVMPD] to the value 1 by entering the digit between the tags:

XEVMPD term will not be used:
	   <xsl:variable name="XEVMPD"></xsl:variable>

XEVMPD term will be used if available:
	<xsl:variable name="XEVMPD">1</xsl:variable>
 
2. NCA Rerouted R3 files

In order to preserve the original sender of an R3 ICSR when converting to an R2 file the variable [NCAREROUTE] has been added. If this is set to the value 1, the original sender organisation provided in N.2.r.2 will be used to populate A.3.2.1.

N.2.r.2 will not be used to populate A.3.2.1
	<xsl:variable name="NCAREROUTE"></xsl:variable>

N.2.r.2 will not be used to populate A.3.2.1
	<xsl:variable name="NCAREROUTE">1</xsl:variable>


R2 --> R3 conversions
-----------
For R2 to R3 conversions (not recommended) the variable [testResMedDRAver] is used to capture the MedDRA version number to be used in the MedDRA coded R3 Lab test name.

MedDRA version 20.0 will be used for lab test names
	<xsl:variable name="testResMedDRAver">20.0</xsl:variable>
	

