import React from 'react';
import PropTypes from "prop-types";

class Comment extends React.Component {
    // constructor(props) {
    //     super(props);
    //   }

      deleteComment(inputId, inputCUrl) {
          console.log("HI");
          console.log('input id: ', inputId); 
          console.log('input c: ', inputCUrl);
          const { changeComment} = this.props;
          changeComment(inputId)
        
          fetch(inputCUrl.toString(), {method: ["DELETE"]})
          .then((response) => {
              if (!response.ok) throw Error(response.statusText);
              return response.json();
          })
          .catch((error) => console.log(error));
      
      }

      render(){
        const { comment} = this.props;
        return(
            <div>
                   
                    <a href = {`/users/${comment.owner}/`}>{comment.owner}</a>{comment.text}
                    {comment.lognameOwnsThis?    <button type = "button" onClick = {() => this.deleteComment(comment.commentid, comment.url)} className="delete-comment-button"> delete comment </button> : ''}
        
            </div>
    
        );

        
    }
    


}
Comment.propTypes = {
  comment: PropTypes.object.isRequired,
  changeComment: PropTypes.func.isRequired
};

export default Comment;