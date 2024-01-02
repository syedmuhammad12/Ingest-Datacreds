<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - B.3 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">
	<!-- Test : 
	E2B(R2): element "test"
	E2B(R3): element "" called from b1
	-->
	<xsl:template match="test">
		<xsl:if test="string-length(testdate) > 0 or string-length(testname) > 0">
			<component typeCode="COMP">
				<observation moodCode="EVN" classCode="OBS">
					<!-- B.3.r.c1-2 Test Name-->
					<xsl:variable name="isMeddraCode">
						<xsl:call-template name="isMeddraCode">
							<xsl:with-param name="code" select="testname"/>
						</xsl:call-template>
					</xsl:variable>
					<xsl:choose>
						<xsl:when test="$isMeddraCode = 'yes'">
							<code code="{testname}" codeSystem="{$oidMedDRA}" codeSystemVersion="{$testResMedDRAver}"/>
						</xsl:when>
						<xsl:otherwise>
							<code>
								<originalText>
									<xsl:value-of select="testname"/>
								</originalText>
							</code>
						</xsl:otherwise>
					</xsl:choose>
					<!-- B.3.r.b Test Date and Time -->
					<xsl:choose>
						<xsl:when test="string-length(testdate) > 0">
							<effectiveTime xsi:type="SXCM_TS" value="{testdate}"/>
						</xsl:when>
						<xsl:otherwise>
							<effectiveTime nullFlavor="UNK"/>
						</xsl:otherwise>
					</xsl:choose>
					<!-- B.3.r.def Results of Tests -->
					<xsl:choose>
						<xsl:when test="number(testresult)">
							<value xsi:type="IVL_PQ">
								<center value="{testresult}">
									<xsl:if test="string-length(testunit) > 0 or not(testunit = 'Not Applicable') or not(testunit = 'NA') or not(testunit = 'N/A')">
										<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="testunit"/></xsl:call-template></xsl:attribute>
									</xsl:if>
									<xsl:if test="string-length(testunit) = 0 or testunit = 'Not Applicable' or testunit = 'NA' or testunit = 'N/A'" >
										<xsl:attribute name="unit">1</xsl:attribute>
									</xsl:if>
								</center>
							</value>
						</xsl:when>
						<xsl:otherwise>
							<value xsi:type="ED">
								<xsl:value-of select="testresult"/>
								<xsl:text> </xsl:text>
								<xsl:if test="string-length(testunit)>0">
									<xsl:value-of select="testunit"/>
								</xsl:if>
							</value>
						</xsl:otherwise>
					</xsl:choose>
					<!-- B.3.r.1 Lowest Result Range -->
					<xsl:if test="string-length(lowtestrange) > 0">
						<referenceRange  typeCode="REFV">
							<observationRange classCode="OBS" moodCode="EVN.CRT">
								<xsl:choose>
									<xsl:when test="number(lowtestrange)">
										<value xsi:type="PQ" value="{lowtestrange}">
											<xsl:attribute name="unit">
												<xsl:choose><!--	<xsl:when test="string-length(testunit) > 0">{<xsl:value-of select="translate(testunit, ' ', '-')"/>}</xsl:when> -->
													<xsl:when test="string-length(testunit) > 0">
														<xsl:call-template name="getMapping">
															<xsl:with-param name="type">UCUM</xsl:with-param>
															<xsl:with-param name="code" select="testunit"/>
														</xsl:call-template>
													</xsl:when>
													<xsl:otherwise>1</xsl:otherwise>
												</xsl:choose>
											</xsl:attribute>
										</value>
										<interpretationCode code="L" codeSystem="2.16.840.1.113883.5.83"/>
									</xsl:when>
									<xsl:otherwise>
										<value xsi:type="ED">
											<xsl:value-of select="lowtestrange"/>
										</value>
										<interpretationCode code="L" codeSystem="2.16.840.1.113883.5.83"/>
									</xsl:otherwise>
								</xsl:choose>
							</observationRange>
						</referenceRange>
					</xsl:if>
					<!-- B.3.r.1 Highest Result Range -->
					<xsl:if test="string-length(hightestrange) > 0">
						<referenceRange typeCode="REFV">
							<observationRange classCode="OBS" moodCode="EVN.CRT">
								<xsl:choose>
									<xsl:when test="number(hightestrange)">
										<value xsi:type="PQ" value="{hightestrange}">
											<xsl:attribute name="unit">
												<xsl:choose><!-- <xsl:when test="string-length(testunit) > 0">{<xsl:value-of select="translate(testunit, ' ', '-')"/>}</xsl:when> -->
													<xsl:when test="string-length(testunit) > 0">
														<xsl:call-template name="getMapping">
															<xsl:with-param name="type">UCUM</xsl:with-param>
															<xsl:with-param name="code" select="testunit"/>
														</xsl:call-template>
													</xsl:when>
													<xsl:otherwise>1</xsl:otherwise>
												</xsl:choose>
											</xsl:attribute>
										</value>
										<interpretationCode code="H" codeSystem="2.16.840.1.113883.5.83"/>
									</xsl:when>
									<xsl:otherwise>
										<value xsi:type="ED">
											<xsl:value-of select="hightestrange"/>
										</value>
										<interpretationCode code="H" codeSystem="2.16.840.1.113883.5.83"/>
									</xsl:otherwise>
								</xsl:choose>
							</observationRange>
						</referenceRange>
					</xsl:if>
					<!-- B.3.r.4 More Information Available -->
					<outboundRelationship2 typeCode="REFR">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$MoreInformationAvailable}" codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="moreinformation = 1">
									<value xsi:type="BL" value="true"/>
								</xsl:when>
								<xsl:when test="moreinformation = 2">
									<value xsi:type="BL" value="false"/>
								</xsl:when>
								<xsl:otherwise>
									<value xsi:type="BL" nullFlavor="UNK"/>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</observation>
			</component>
		</xsl:if>
	</xsl:template>
	
	<!-- B.3.r.3 Test Comments in an additional test occurrence -->
	<xsl:template match="resultstestsprocedures">
		<xsl:if test="string-length(.) > 0">
			<component typeCode="COMP">
				<observation moodCode="EVN" classCode="OBS">
					<code nullFlavor="NA"/>
					<outboundRelationship2 typeCode="PERT">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Comment}" codeSystem="{$oidObservationCode}"/>
							<value xsi:type="ED">
								<xsl:value-of select="."/>
							</value>
						</observation>
					</outboundRelationship2>
				</observation>
			</component>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
