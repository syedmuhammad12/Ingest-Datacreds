<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - A.3 Part)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields

		Version:		1.1
		Date:			04/08/2017
		Status:			Final
		Author:			Nick Halsey (EU)
		Amendment:	Addition of code to allow N.2.r.2 to be copied into A.3.2.1 for NCA rerouted R3 files.
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!--	A.3.1. Sender -->
	<xsl:template match="hl7:assignedEntity" mode="sender">
		<sendertype>
			<xsl:choose>
				<xsl:when test="hl7:code/@code = 7">6</xsl:when>
				<xsl:otherwise><xsl:value-of select="hl7:code/@code"/></xsl:otherwise>
			</xsl:choose>
		</sendertype>
		<senderorganization>
		<xsl:choose>
				<xsl:when test="$NCAREROUTE =1">
					<xsl:value-of select="../../../../../../../hl7:sender/hl7:device/hl7:id/@extension"/>
				</xsl:when>
				<xsl:otherwise>			
					<xsl:if test="hl7:representedOrganization/hl7:assignedEntity/hl7:representedOrganization/hl7:name/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string" select="hl7:representedOrganization/hl7:assignedEntity/hl7:representedOrganization/hl7:name"/>
						<xsl:with-param name="string-length">60</xsl:with-param>
					</xsl:call-template>
			</xsl:otherwise>	
			</xsl:choose>
		</senderorganization>
		<senderdepartment>
			<xsl:if test="hl7:representedOrganization/hl7:name/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string" select="hl7:representedOrganization/hl7:name"/>
				<xsl:with-param name="string-length">60</xsl:with-param>
			</xsl:call-template>
		</senderdepartment>
		<sendertitle>
			<xsl:if test="hl7:assignedPerson/hl7:name/hl7:prefix/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string" select="hl7:assignedPerson/hl7:name/hl7:prefix"/>
				<xsl:with-param name="string-length">10</xsl:with-param>
			</xsl:call-template>
		</sendertitle>
		<sendergivename>
			<xsl:if test="hl7:assignedPerson/hl7:name/hl7:given[1]/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string" select="hl7:assignedPerson/hl7:name/hl7:given[1]"/>
				<xsl:with-param name="string-length">35</xsl:with-param>
			</xsl:call-template>
		</sendergivename>
		<sendermiddlename>
			<xsl:if test="hl7:assignedPerson/hl7:name/hl7:given[2]/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string" select="hl7:assignedPerson/hl7:name/hl7:given[2]"/>
				<xsl:with-param name="string-length">15</xsl:with-param>
			</xsl:call-template>
		</sendermiddlename>
		<senderfamilyname>
			<xsl:if test="hl7:assignedPerson/hl7:name/hl7:family/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string" select="hl7:assignedPerson/hl7:name/hl7:family"/>
				<xsl:with-param name="string-length">35</xsl:with-param>
			</xsl:call-template>
		</senderfamilyname>
		<senderstreetaddress>
			<xsl:if test="hl7:addr/hl7:streetAddressLine/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:value-of select="hl7:addr/hl7:streetAddressLine"/>
		</senderstreetaddress>
		<sendercity>
			<xsl:if test="hl7:addr/hl7:city/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:value-of select="hl7:addr/hl7:city"/>
		</sendercity>
		<senderstate>
			<xsl:if test="hl7:addr/hl7:state/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:value-of select="hl7:addr/hl7:state"/>
		</senderstate>
		<senderpostcode>
			<xsl:if test="hl7:addr/hl7:postalCode/@nullFlavor = 'MSK'">PRIVACY</xsl:if>
			<xsl:value-of select="hl7:addr/hl7:postalCode"/>
		</senderpostcode>
		<sendercountrycode>
			<xsl:value-of select="hl7:assignedPerson/hl7:asLocatedEntity/hl7:location/hl7:code/@code"/>
		</sendercountrycode>
		<xsl:choose>
			<xsl:when test="string-length(hl7:telecom[starts-with(@value, 'tel:')]/@value) > 14">
				<sendertel><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'tel:')]/@value, 'tel:'), 1, 14),'+ -',''),1,10) "/></sendertel>
				<sendertelextension><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'tel:')]/@value, 'tel:'), 1, 19),'+ -',''),11,5) "/></sendertelextension>
			</xsl:when>
			<xsl:otherwise>
				<sendertel><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'tel:')]/@value, 'tel:'), 1, 14),'+ -',''),1,10) "/></sendertel>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="string-length(hl7:telecom[starts-with(@value, 'fax:')]/@value) > 14">
				<senderfax><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'fax:')]/@value, 'fax:'), 1, 14),'+ -',''),1,10) "/></senderfax>
				<senderfaxextension><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'fax:')]/@value, 'fax:'), 1, 19),'+ -',''),11,5) "/></senderfaxextension>
			</xsl:when>
			<xsl:otherwise>
			<senderfax><xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, 'fax:')]/@value, 'fax:'), 1, 14),'+ -',''),1,10) "/></senderfax>
			</xsl:otherwise>
		</xsl:choose>
		
		<senderemailaddress>
			<xsl:call-template name="telecom2">
				<xsl:with-param name="type">mailto:</xsl:with-param>
				<xsl:with-param name="len">100</xsl:with-param>
			</xsl:call-template>
		</senderemailaddress>
	</xsl:template>
	
	<xsl:template name="telecom">
		<xsl:param name="type"/>
		<xsl:param name="len"/>
				<xsl:value-of select="substring(translate(substring(substring-after(hl7:telecom[starts-with(@value, $type)]/@value, $type), 1, $len),'+ -',''),1,10) "/>
	</xsl:template>	
	<xsl:template name="telecom2">
		<xsl:param name="type"/>
		<xsl:param name="len"/>
		<xsl:value-of select="substring(substring-after(hl7:telecom[starts-with(@value, $type)]/@value, $type), 1, $len)"/>
	</xsl:template>
</xsl:stylesheet>
