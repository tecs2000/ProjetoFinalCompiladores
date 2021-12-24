/* *******************************************************************
 * Copyright (c) 2021 Universidade Federal de Pernambuco (UFPE).
 * 
 * This file is part of the Compilers course at UFPE.
 * 
 * During the 1970s and 1980s, Hewlett-Packard used RPN in all 
 * of their desktop and hand-held calculators, and continued to 
 * use it in some models into the 2020s. In computer science, 
 * reverse Polish notation is used in stack-oriented programming languages 
 * such as Forth, STOIC, PostScript, RPL and Joy.
 *  
 * Contributors: 
 *     Henrique Rebelo      initial design and implementation 
 *     http://www.cin.ufpe.br/~hemr/
 * ******************************************************************/

package postfix.interpreter;

import java.util.HashMap;

import postfix.ast.Expr;
import postfix.ast.Expr.Id;

/**
 * @author Henrique Rebelo
 */
public class Interpreter implements Expr.Visitor<Integer> {
	
	public final HashMap<String, String> env;
	public Interpreter(HashMap<String, String> env){ this.env = env; }
	  
	public int interp(Expr expression) { 
		int value = evaluate(expression);
		
		return value;
	}
	
	@Override
	public Integer visitIdExpr(Id expr) {
		try {
			return Integer.parseInt(env.get(expr.value));
		}
		catch (NumberFormatException e){
			throw new InterError("Variavel "+ expr.value + " foravariável fora do escopo");
		}
	}
	
	@Override
	public Integer visitNumberExpr(Expr.Number expr) {
		return Integer.parseInt(expr.value);
	}

	@Override
	public Integer visitBinopExpr(Expr.Binop expr) {
		int right = evaluate(expr.right); 
		int result = 0;

		switch (expr.operator.type) {
		case PLUS:
			result = evaluate(expr.left) + right;
			break;
		case MINUS:
			result = evaluate(expr.left) - right;
			break;
		case SLASH:
			result = evaluate(expr.left) / right;
			break;
		case STAR:
			result = evaluate(expr.left) * right;
			break;
			
		case EQUAL:
			env.put(((Expr.Id)expr.left).value, Integer.toString(right));
			result = right;
			break;
			
		default:
			break;
		}

		return result;
	}

	private int evaluate(Expr expr) {
		return expr.accept(this);
	}
}
